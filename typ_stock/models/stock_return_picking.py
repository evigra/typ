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

    @api.model
    def default_get(self, fields):
        """To get default values for the product to be returned. Include
        product, qty and move related
        :param fields List of fields for which we want default values
        :return A dictionary with default values for all field in ``fields``
        """
        result = []
        context = self._context
        if len(context.get('active_ids', [])) > 1:
            raise exceptions.Warning(
                _('Warning!'),
                _("You may only return one picking at a time!"))
        res = super(StockReturnPicking, self).default_get(fields)
        if 'product_return_moves' not in fields:
            return res
        record_id = context.get('active_id', False)
        pick_obj = self.env['stock.picking']
        uom = self.env['product.uom']
        pick = pick_obj.browse(record_id)

        for move in pick.move_lines:
            qty = pick_obj.validate_return_customer_qty(move)

            move_qty = uom._compute_qty(
                move.product_id.uom_id.id,
                qty,
                move.product_uom.id,
            )

            result.append(
                {'product_id': move.product_id.id,
                 'quantity': move_qty,
                 'move_id': move.id})

        res.update({'product_return_moves': result})

        return res

    @api.multi
    def _create_returns(self):
        """When picking is return, the value of field purchase_line_id in
        moves is lost, here this value is set in all picking move.
        """
        res = super(StockReturnPicking, self)._create_returns()
        new_picking = self.env['stock.picking'].browse(res[0])
        for move in new_picking.move_lines:
            move.write({'purchase_line_id':
                        move.origin_returned_move_id.purchase_line_id.id})
        return res
