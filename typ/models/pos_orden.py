# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _get_usage_selection(self):
        return self.env['res.partner']._get_usage_selection()

    l10n_mx_edi_usage = fields.Selection(
        _get_usage_selection, 'Usage',
        help='This usage will be used instead of the default one for invoices.'
    )

    def _prepare_invoice(self):
        res = super(PosOrder, self)._prepare_invoice()
        journal = self.statement_ids.filtered('journal_id').journal_id
        res.update({
            'l10n_mx_edi_usage': self.l10n_mx_edi_usage,
            'l10n_mx_edi_payment_method_id': journal.l10n_mx_edi_payment_method_id.id, # noqa
        })
        return res

    @api.multi
    def action_pos_order_invoice(self):
        return super(
            PosOrder,
            self.with_context(l10n_mx_edi_avoid_partner_defaults=True)
        ).action_pos_order_invoice()
