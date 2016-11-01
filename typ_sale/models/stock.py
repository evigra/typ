# coding: utf-8

from openerp import api, models


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        res.update({
            'payment_term': move.picking_id.sale_id.payment_term.id,
            'type_payment_term': move.picking_id.sale_id.type_payment_term, })
        return res
