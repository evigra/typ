# -*- coding: utf-8 -*-

from openerp import api, models


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def propagate_picking_transfer(self):
        """If stock_move is done verify if it have to propagate transfer to
        move_dest_id.
        """
        if self.state == 'assigned' and\
                self.move_orig_ids.filtered(lambda dat: dat.state == 'done')\
                and self.rule_id.propagate_transfer:
            picking = self.picking_id
            ctx = {
                'active_id': picking.id,
                'active_ids': [picking.id],
                'active_model': 'stock.picking',
            }
            wizard_transfer_id = self.env['stock.transfer_details'].\
                with_context(ctx).create({'picking_id': picking.id})
            wizard_transfer_id.do_detailed_transfer()
