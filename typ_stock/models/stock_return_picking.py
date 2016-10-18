# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp import exceptions


class StockReturnPicking(models.TransientModel):
    """Class inherit wizard Stock Return Picking
    """

    _inherit = "stock.return.picking"

    @api.multi
    def create_returns(self):
        quant_obj = self.env['stock.quant']
        uom = self.env['product.uom']

        for line in self.product_return_moves:
            # Sum the quants in that location that can be returned
            # (they should have been moved by the moves that were included in
            # the returned picking)
            quantity = sum(quant.qty for quant in quant_obj.search([
                ('history_ids', 'in', line.move_id.id),
                ('qty', '>', 0.0),
                ('location_id', 'child_of', line.move_id.location_dest_id.id)
            ]).filtered(
                lambda quant: not quant.reservation_id or
                quant.reservation_id.origin_returned_move_id != line.move_id)
            )

            quantity_user = uom._compute_qty(line.move_id.product_uom.id,
                                             line.quantity,
                                             line.product_id.uom_id.id)

            if quantity < quantity_user:
                raise exceptions.Warning(
                    _('Warning!'),
                    _('The return of the product %s, exceeds the amount '
                        'invoiced') % (line.move_id.product_id.name)
                )
        return super(StockReturnPicking, self).create_returns()
