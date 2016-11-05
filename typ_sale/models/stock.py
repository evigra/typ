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


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def _prepare_procurement_from_move(self, move):
        """Inherit to reassign origin field in procurement order"""
        res = super(StockMove, self)._prepare_procurement_from_move(move)
        order = move.procurement_id._get_sale_line_id().order_id
        if order:
            res.update({'origin': order.name})
        return res
