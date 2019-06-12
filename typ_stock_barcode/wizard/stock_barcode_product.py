# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockBarcodeNotracking(models.TransientModel):
    _name = "stock.barcode.notracking"
    _inherit = ['barcodes.barcode_events_mixin']
    _description = """
        Wizard to scan products with no tracking and for specific product
    """

    picking_id = fields.Many2one('stock.picking')
    product_id = fields.Many2one('product.product')
    qty_reserved = fields.Float()
    qty_done = fields.Float()
    default_move_id = fields.Many2one('stock.move')
    stock_barcode_product_line_ids = fields.One2many(
        'stock.barcode.product.line', 'stock_barcode_product_id')

    @api.model
    def default_get(self, fields_list):
        res = super(StockBarcodeNotracking, self).default_get(fields_list)
        qty_reserved = 0.0
        qty_done = 0.0
        candidates_ids = self.env.context.get('candidates')
        if 'stock_barcode_product_line_ids' in fields_list and candidates_ids:
            candidates = self.env['stock.move.line'].browse(candidates_ids)
            lines = []
            res['default_move_id'] = candidates[0].move_id.id
            for ml in candidates:
                lines.append({
                    'product_barcode': ml.product_id.barcode,
                    'qty_reserved': ml.product_uom_qty,
                    'qty_done': ml.qty_done + 1,
                    'move_line_id': ml.id,
                })
                qty_reserved += ml.product_uom_qty
                qty_done += ml.qty_done
            res['stock_barcode_product_line_ids'] = [(0, 0, x) for x in lines]
        if 'qty_reserved' in fields_list:
            res['qty_reserved'] = qty_reserved
        if 'qty_done' in fields_list:
            res['qty_done'] = qty_done
        return res

    @api.multi
    def _update_quantity_done(self):
        self.ensure_one()
        self.qty_done = sum(
            self.stock_barcode_product_line_ids.mapped('qty_done'))

    @api.multi
    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        suitable_line = self.stock_barcode_product_line_ids.filtered(
            lambda l: l.product_barcode == barcode or not l.product_barcode)
        vals = {}
        if not suitable_line:
            raise UserError(
                _('Be sure that you are scanning the same product'))
        vals['product_barcode'] = barcode
        vals['qty_done'] = suitable_line[0].qty_done + 1
        suitable_line[0].update(vals)
        self.qty_done += 1

    @api.multi
    def validate_product_set(self):
        self.ensure_one()
        for line in self.stock_barcode_product_line_ids.filtered(
                'product_barcode'):
            vals = {}
            vals['qty_done'] = line.qty_done
            if line.move_line_id:
                line.move_line_id.write(vals)
            elif self.default_move_id:
                vals.update({
                    'picking_id': self.picking_id.id,
                    'move_id': self.default_move_id.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.default_move_id.product_uom.id,
                })
                self.env['stock.move.line'].create(vals)
            else:
                vals.update({
                    'picking_id': self.picking_id.id,
                    'product_id': self.product_id.id,
                    'product_uom_id': self.product_id.uom_id.id,
                })
                new_move = self.env['stock.move'].create({
                    'name': self.picking_id.name,
                    'picking_id': self.picking_id.id,
                    'picking_type_id': self.picking_id.picking_type_id.id,
                    'product_id': self.product_id.id,
                    'product_uom': self.product_id.uom_id.id,
                    'move_line_ids': [(0, 0, vals)]
                })
                self.default_move_id = new_move


class StockBarcodeProductLine(models.TransientModel):
    _name = "stock.barcode.product.line"
    _description = "Line of LN/SN scanned of a product"

    product_barcode = fields.Char()
    qty_reserved = fields.Float('Quantity Reserved')
    qty_done = fields.Float('Quantity Done')
    stock_barcode_product_id = fields.Many2one('stock.barcode.notracking')
    move_line_id = fields.Many2one('stock.move.line')

    @api.onchange('qty_done')
    def onchange_qty_done(self):
        self.stock_barcode_product_id._update_quantity_done()
