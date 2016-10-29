# coding: utf-8

from openerp import api, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.multi
    def action_picking_create(self):
        for order in self:
            res = super(PurchaseOrder, order).action_picking_create()
            if self.origin:
                new_origin = self.origin + ':' + self.name
                self.env['stock.picking'].browse(res).write(
                    {'origin': new_origin})
            return res
