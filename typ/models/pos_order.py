from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    l10n_mx_edi_usage = fields.Selection(
        selection=lambda self: self._get_usage_selection(),
        string="Usage",
        help="This usage will be used instead of the default one for invoices.",
    )

    def _get_usage_selection(self):
        return self.env["res.partner"]._get_usage_selection()

    @api.model
    def _order_fields(self, ui_order):
        res = super()._order_fields(ui_order)
        if "l10n_mx_edi_usage" in ui_order:
            res["l10n_mx_edi_usage"] = ui_order["l10n_mx_edi_usage"]
        return res

    def _prepare_invoice_vals(self):
        res = super()._prepare_invoice()
        max_pay = max(self.statement_ids.mapped("amount"))
        journal = self.statement_ids.filtered(lambda s: s.amount == max_pay)[0]
        payment_method = (
            journal.journal_id.l10n_mx_edi_payment_method_id.id
            if journal.journal_id.l10n_mx_edi_payment_method_id
            else False
        )
        res.update(
            {
                "l10n_mx_edi_usage": self.l10n_mx_edi_usage,
                "l10n_mx_edi_payment_method_id": payment_method,
            }
        )
        return res

    def action_pos_order_invoice(self):
        return super(
            PosOrder,
            self.with_context(l10n_mx_edi_avoid_partner_defaults=True),
        ).action_pos_order_invoice()
