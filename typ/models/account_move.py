import base64
import io
import logging
import zipfile

from odoo import _, api, fields, models

# from odoo.addons.l10n_mx_edi.tools.run_after_commit import run_after_commit  -> TODO: review on v14.0


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
    invoice_user_id = fields.Many2one(tracking=True)
    validation_date = fields.Date(
        string="Invoice validation date",
        copy=False,
        readonly=True,
        help="This date indicates when the invoice was validated",
    )
    date_paid = fields.Date(
        "Payment date",
        copy=False,
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

    @api.model
    def line_get_convert(self, line, part):
        res = super().line_get_convert(line, part)
        res["guide_line_id"] = line.get("guide_line_id", False)
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

    def my_invoices_zip(self):
        invoice_xml = self.l10n_mx_edi_retrieve_last_attachment()
        attachment_id = ""
        invoice_pdf = self.retrieve_last_invoice()

        attachments_exists = self.retrieve_invoices_zip()

        if attachments_exists:
            attachment_id = attachments_exists
        elif invoice_xml is not None and invoice_pdf is not None:
            attachment_id = self.create_zip(invoice_xml, invoice_pdf)
        elif invoice_xml is not None and invoice_pdf is None:
            attachment_id = invoice_xml
        else:
            attachment_id = invoice_pdf

        return attachment_id

    def retrieve_invoices(self):
        domain = [
            ("res_id", "=", self.id),
            ("res_model", "=", "account.move"),
            ("mimetype", "=", "application/pdf"),
            ("name", "like", "%.pdf"),
        ]
        return self.env["ir.attachment"].search(domain)

    def retrieve_last_invoice(self):
        attachment_ids = self.retrieve_invoices()
        return attachment_ids and attachment_ids[0] or None

    def retrieve_invoices_zip(self):
        domain = [
            ("res_id", "=", self.id),
            ("mimetype", "=", "application/zip"),
        ]
        attachments = self.env["ir.attachment"].search(domain)
        return attachments

    def create_zip(self, invoice_xml, invoice_pdf):
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, "w") as myzip:
            myzip.writestr(invoice_xml.name, base64.b64decode(invoice_xml.datas))
            myzip.writestr(invoice_pdf.name, base64.b64decode(invoice_pdf.datas))
            myzip.close()
            zip_name = invoice_xml.name.replace(".xml", ".zip")
            values = {
                "name": zip_name,
                "type": "binary",
                "mimetype": "application/zip",
                "public": False,
                "db_datas": base64.b64encode(zip_stream.getvalue()),
                "res_id": invoice_xml.res_id,
                "datas_fname": zip_name,
            }
        attachment_id = self.env["ir.attachment"].create(values)
        return attachment_id

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
