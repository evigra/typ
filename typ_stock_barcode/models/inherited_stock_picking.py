# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def get_po_to_split_from_barcode_no_tracking(self, barcode):
        """ Returns the no tracking visible product wizard's action for the
        move line matching the barcode. This method is intended to be called by
        the `picking_no_tracking_barcode_handler` javascript widget when the
        user scans the barcode of a tracked product.
        """
        candidates = self.env['stock.move.line'].search([
            ('picking_id', 'in', self.ids),
            ('product_barcode', '=', barcode),
        ])
        if not candidates:
            raise UserError(
                _('Scanned product not found.'))

        product_id = candidates.mapped('product_id')

        action_ctx = dict(
            self.env.context, default_picking_id=self.id,
            default_product_id=product_id.id, candidates=candidates.ids,
            default_barcode=barcode)
        view_id = self.env.ref(
            'typ_stock_barcode.view_barcode_notracking_form').id
        return {
            'name': _('%s set.') % product_id.display_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.barcode.notracking',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': action_ctx}
