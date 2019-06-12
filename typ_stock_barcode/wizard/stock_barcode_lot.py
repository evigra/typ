# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo.exceptions import UserError


class StockBarcodeLot(models.TransientModel):
    _inherit = 'stock_barcode.lot'

    def on_barcode_scanned(self, barcode):
        picking_type = self.picking_id.picking_type_id
        product = self.product_id
        if picking_type.code != 'incoming' and product.tracking != 'none':
            lot = self.env['stock.production.lot'].search([
                ('product_id', '=', product.id),
                ('name', '=', barcode)], limit=1)
            if (not lot and picking_type.use_create_lots and
                    picking_type.use_existing_lots):
                raise UserError(_(
                    "Scanned number it's not a valid Serial number."))
        # Allow create Serial/Lot numbers
        return super(StockBarcodeLot, self).on_barcode_scanned(barcode)
