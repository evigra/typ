from odoo import exceptions, models, api, fields, _


class AccountInvoice(models.Model):

    _inherit = "account.move"

    invoice_user_id = fields.Many2one(
        "res.users",
        tracking=True,
    )
    validation_date = fields.Date(
        "Invoice validation date", help="This date indicate when the invoice was validated"
    )
    date_paid = fields.Date(
        "Payment date", index=True, copy=False, help="This date indicate when the invoice was paid"
    )
    supplier_invoice_number = fields.Char(
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="The reference of this invoice is provided by the supplier",
    )


    # @api.onchange("partner_id", "journal_id")
    def _onchange_limit_credit(self):  # TODO: Check if this could be sent to the main credit app.
        """Show warning message if partner selected has no credit limit."""
        is_cash = (
            self.type_payment_term in ("cash", "postdated_check")
            or not self.partner_id.property_payment_term_id
            or self.partner_id.property_payment_term_id.payment_type == "cash"
        )
        if not self.need_verify_limit_credit() or is_cash:
            return {}
        ctx = {"new_amount": self.amount_total, "new_currency": self.currency_id.id, "journal_id": self.journal_id.id}
        res_partner = self.env["res.partner"].with_context(ctx)
        allowed_sale = res_partner.browse(self.partner_id.id).allowed_sale
        if not self.partner_id or allowed_sale:
            return {}
        credit_overloaded = res_partner.browse(self.partner_id.id).credit_overloaded
        overdue_credit = (
            res_partner.with_context({"journal_id": self.journal_id.id}).browse(self.partner_id.id).overdue_credit
        )
        msg = _("The partner ")
        if credit_overloaded:
            msg = msg + _("%s has credit overloaded")
            if overdue_credit:
                msg = msg + _(" and has overdue invoices")
        elif overdue_credit:
            msg = msg + _("%s has overdue invoices")
        msg = msg + _(". Please request payment or sell cash!")
        warning = {
            "title": _("Warning!"),
            "message": ((msg) % self.partner_id.name),
        }
        return {"warning": warning}

    # @api.model
    # def invoice_validate(self):
    #     res = super().invoice_validate()
    #     validation_date = fields.Date.context_today(self)
    #     self.write({"validation_date": validation_date})
    #     return res

    # def confirm_paid(self):
    #     res = super().confirm_paid()
    #     date_paid = fields.Date.context_today(self)
    #     self.write({"date_paid": date_paid})
    #     return res

    # def _l10n_mx_edi_get_payment_policy(self):
    #     """Inherit Method to change the Payment Method to PPD, if the payment
    #     term is Post-dated Checks"""
    #     self.ensure_one()
    #     version = self.l10n_mx_edi_get_pac_version()
    #     res = super()._l10n_mx_edi_get_payment_policy()
    #     if version != "3.3" or self.type_payment_term != "postdated_check":
    #         return res
    #     return "PPD"
