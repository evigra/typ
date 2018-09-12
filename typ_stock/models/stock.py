# coding: utf-8

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        for move in self.product_return_moves:
            product_qty = self.picking_id.returned_ids.mapped(
                'move_lines').filtered(
                    lambda dat: dat.product_id.id == move.product_id.id and
                    dat.state != 'cancel'
                ).mapped('product_qty')
            quantity = move.move_id.product_qty - sum(product_qty)
            quantity = float_round(
                quantity, precision_rounding=move.move_id.product_uom.rounding)
            if move.quantity > quantity:
                raise UserError(_(
                    '[Product: %s, To return: %s]'
                    ' You can not return more quantity than delivered')
                    % (move.product_id.name, quantity))
        return super(ReturnPicking, self)._create_returns()
