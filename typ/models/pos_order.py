from odoo import models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_vals(self):
        res = super()._prepare_invoice_vals()
        if self.payment_ids:
            max_pay = max(self.payment_ids.mapped("amount"))
            payment_method = self.payment_ids.filtered(lambda s: s.amount == max_pay)[:1].payment_method_id
            l10n_mx_payment_method = payment_method.l10n_mx_edi_payment_method_id.id
            res["l10n_mx_edi_payment_method_id"] = l10n_mx_payment_method
        return res

    def action_pos_order_invoice(self):
        return super(
            PosOrder,
            self.with_context(l10n_mx_edi_avoid_partner_defaults=True),
        ).action_pos_order_invoice()
