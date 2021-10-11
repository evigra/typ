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
        res = super()._prepare_invoice_vals()
        if self.payment_ids:
            max_pay = max(self.payment_ids.mapped("amount"))
            payment_method = self.payment_ids.filtered(lambda s: s.amount == max_pay)[:1].payment_method_id
            l10n_mx_payment_method = payment_method.l10n_mx_edi_payment_method_id.id
            res['l10n_mx_edi_payment_method_id'] = l10n_mx_payment_method
        if self.l10n_mx_edi_usage:
            res['l10n_mx_edi_usage'] = self.l10n_mx_edi_usage
        return res

    def action_pos_order_invoice(self):
        return super(
            PosOrder,
            self.with_context(l10n_mx_edi_avoid_partner_defaults=True),
        ).action_pos_order_invoice()
