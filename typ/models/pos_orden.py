# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string="Payment Method",
        help='This payment method will be used by default in the related '
        'documents (invoices, payments, and bank statements).')

    def _get_usage_selection(self):
        return self.env['res.partner']._get_usage_selection()

    l10n_mx_edi_usage = fields.Selection(
        _get_usage_selection, 'Usage',
        help='This usage will be used instead of the default one for invoices.'
    )

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        res.update({
            'l10n_mx_edi_usage': self.l10n_mx_edi_usage,
            'l10n_mx_edi_payment_method_id': self.l10n_mx_edi_payment_method_id
        })
        return res

    @api.multi
    def action_pos_order_invoice(self):
        return super(
            PosOrder,
            self.with_context(l10n_mx_edi_avoid_partner_defaults=True)
        ).action_pos_order_invoice()
