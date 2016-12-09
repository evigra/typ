# coding: utf-8

from openerp import api, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    def action_picking_create(self):
        for order in self:
            res = super(PurchaseOrder, order).action_picking_create()
            self.env['stock.picking'].browse(res).write(
                {'picking_shipment_date': order.shipment_date})
            if self.origin:
                new_origin = self.origin + ':' + self.name
                self.env['stock.picking'].browse(res).write(
                    {'origin': new_origin})
            return res

    @api.model
    def _prepare_order_line_move(self,
                                 order, order_line, picking_id, group_id):
        res = super(PurchaseOrder, order)._prepare_order_line_move(
            order, order_line, picking_id, group_id)
        res[0].update({'shipment_date': order_line.shipment_date})
        return res
