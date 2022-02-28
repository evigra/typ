import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    # Only the partner's payment term and immediate ones may be selected in customer invoices
    partner_payment_term_id = fields.Many2one("account.payment.term", compute="_compute_partner_payment_term_id")
    invoice_payment_term_id = fields.Many2one(
        domain="""[
            '|', '|',
            ('is_immediate', '=', True),
            ('id', '=', partner_payment_term_id),
            (move_type not in ('out_invoice', 'out_refund', 'out_receipt'), '=', True),
        ]""",
    )
    # Due date won't be editable, even in draft
    invoice_date_due = fields.Date(states=None)
    invoice_user_id = fields.Many2one(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    validation_date = fields.Date(
        string="Invoice validation date",
        copy=False,
        readonly=True,
        help="This date indicates when the invoice was validated",
    )
    date_paid = fields.Date(
        "Payment date",
        compute="_compute_amount",
        store=True,
        help="This date indicates when the invoice was paid",
    )
    supplier_invoice_number = fields.Char(
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="The reference of this invoice is provided by the vendor",
    )
    stock_landed_cost_id = fields.Many2one("stock.landed.cost")
    guide_line_id = fields.Many2one("stock.landed.cost.guide.line", help="Guide line associated to this" " move")

    @api.depends("partner_id", "journal_id")
    def _compute_partner_payment_term_id(self):
        for move in self:
            move = move.with_company(move.journal_id.company_id)
            move.partner_payment_term_id = move.partner_id.property_payment_term_id

    @api.depends(
        "restrict_mode_hash_table",
        "state",
        # This one was added
        "payment_id",
    )
    def _compute_show_reset_to_draft_button(self):
        """Consider groups and payments to determine if button "Reset to Draft" should be visible

        It works as follows:
        - If natively not visible, then leave it as it is
        - If it's a payment, the group "Can cancel payments" must be enabled
        - Otherwise, the group "Can cancel invoices" must be enabled
        """
        res = super()._compute_show_reset_to_draft_button()
        can_cancel_invoice = self.env.user.has_group("typ.res_group_cancel_invoice")
        can_cancel_payment = self.env.user.has_group("typ.res_group_button_cancel_payment")
        for move in self.filtered("show_reset_to_draft_button"):
            move.show_reset_to_draft_button = can_cancel_payment if move.payment_id else can_cancel_invoice
        return res

    def _post(self, soft=True):
        """Perform some tasks when posting

        The following is performed:
        - Write validation date
        - If It's an invoice coming from the PoS, send it by e-mail automatically
        """
        to_post = super()._post(soft)
        to_post.write({"validation_date": fields.Date.context_today(self)})
        to_post.filtered("pos_order_ids").send_invoice_mail()
        return to_post

    def send_invoice_mail(self):
        """Try to send the XML and Invoice report by email to customer.
        If a problem is found, a new message will be added
        with the error in the invoice."""
        for record in self:
            if not record.partner_id.email:
                record.message_post(
                    subject=_("Error when try to send invoice by email"),
                    body=_(
                        "<h2>Error when try to send invoice by email</h2>"
                        "<hr>Partner has not email. Please set that value."
                        "</hr>"
                    ),
                )
                continue
            message = record.action_invoice_sent()
            mail = self.env["mail.compose.message"].with_context(message.get("context", {})).create({})
            tmp = self.env.ref("account.email_template_edi_invoice", False)
            # If not wkhtmltopdf executable of some error in the onchange
            # (for example trying to render the email custom template) the
            # invoice can be signed but not updated the invoice record, this
            # need to be managed more secure, that's why this try.
            data = {}
            errored = False
            try:
                data = mail.onchange_template_id(tmp.id, None, "account.move", record.id).get("value", {})
            except BaseException as e:
                _logger.info("invoice not sent even if configured. %s")
                data.update({"subject": str(e)})
                errored = True
            mail.write(
                {
                    "body": data.get(
                        "body",
                        "Invoice not sent because an error rendering or generating the email",
                    ),
                    "partner_ids": data.get("partner_ids", []),
                    "email_from": data.get("email_from", ""),
                    "attachment_ids": data.get("attachment_ids", []),
                    "subject": data.get("subject", ""),
                }
            )
            mail.with_context(mark_invoice_as_sent=True).send_mail()
            mail = self.env["mail.mail"].search(
                [
                    ("res_id", "=", record.id),
                    ("model", "=", record._name),
                    ("subject", "=", data.get("subject", "")),
                ],
                limit=1,
            )
            if not mail or errored:
                continue
            record.write({"is_move_sent": False})
            record.message_post(
                subject=_("Error when try send invoice by email"),
                # Validate that mail exists, because the search can return a
                # mails list with some False
                body="<br>".join(["- " + msg.failure_reason for msg in mail if msg.failure_reason]),
            )

    def _check_credit_limit(self):
        """Pass warehouse and journal by context so they're considered when computing credit limit"""
        wo_credit = self.browse()
        for invoice in self:
            ctx = {
                "credit_limit_warehouse_id": invoice.team_id.default_warehouse_id.id,
                "credit_limit_journal_id": invoice.journal_id.id,
            }
            invoice = invoice.with_context(**ctx)
            wo_credit |= super(AccountMove, invoice)._check_credit_limit()
        return wo_credit

    @api.depends(
        "line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.debit",
        "line_ids.credit",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        "line_ids.payment_id.state",
        "line_ids.full_reconcile_id",
    )
    def _compute_amount(self):
        res = super()._compute_amount()
        for move in self:
            if (
                not move.is_invoice(include_receipts=True)
                or move.state != "posted"
                or move.payment_state in ("not_paid", "partial")
            ):
                move.date_paid = False
                continue
            reconciled_entries = move._get_reconciled_entries()
            # it's the default order, but if we don't pass a specific order to sorted(), an extra
            # search will be run, so better use cached values
            latest_entry = reconciled_entries.sorted(lambda m: (m.date, m.name, m.id), reverse=True)[:1]
            move.date_paid = latest_entry.date
        return res

    def _get_reconciled_entries(self):
        """Retrieve the reconciled entries that pay this invoice

        This is similar to method that retrieves reconciled payments, but considering also
        journal entries without payment, e.g. PoS payments.
        """
        reconciled_lines = self.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        reconciled_amls = (
            reconciled_lines.matched_debit_ids.debit_move_id | reconciled_lines.matched_credit_ids.credit_move_id
        )
        reconciled_entries = reconciled_amls.move_id
        return reconciled_entries
