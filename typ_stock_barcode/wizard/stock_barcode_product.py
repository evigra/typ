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
    qty_done = fields.Float('Manually Quantity Done')
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
                qty_done = (ml.qty_done + 1 if ml.qty_done < ml.product_uom_qty
                            else ml.qty_done)
                qty_reserved = ml.product_uom_qty
                lines.append({
                    'line_product_barcode': ml.product_id.barcode,
                    'qty_reserved': qty_reserved,
                    'qty_done': qty_done,
                    'move_line_id': ml.id,
                })
            res['stock_barcode_product_line_ids'] = [(0, 0, x) for x in lines]
        if 'qty_done' in fields_list:
            res['qty_done'] = False
        return res

    @api.onchange('qty_done')
    def onchange_quantity_done(self):
        barcode = self.env.context.get('default_barcode')
        suitable_lines = self.stock_barcode_product_line_ids.filtered(
            lambda l: l.line_product_barcode == barcode)
        if len(suitable_lines) > 1:
            list_diff = suitable_lines.filtered(
                lambda x: x.qty_done - x.qty_reserved != 0).mapped(
                    lambda x: [x, x.qty_reserved - x.qty_done])
            res = min(list_diff, key=lambda x: x[1], default=[])
            suitable_lines = res[0] if res else suitable_lines[0]
        qty_done = (self.qty_done if self.qty_done != 0 else
                    suitable_lines.qty_done)
        suitable_lines.qty_done = qty_done
        if suitable_lines.qty_done > suitable_lines.qty_reserved:
            raise UserError(
                _("You cannot fill more than the requested quantity"))

    @api.multi
    def on_barcode_scanned(self, barcode):
        """This function is called when no product_barcode is not found on UI,
        This is in order to make a post-process or search under a different
        criteria that product_barcode field

        Note: product_barcode is the first field consulted from js side if
        founded a record that matches the barcode scanned on product_barcode
        field it will try to increment only by js
        """
        self.ensure_one()
        suitable_lines = self.stock_barcode_product_line_ids.filtered(
            lambda l: l.line_product_barcode == barcode)
        # If more than one line per product, then increment the one that is
        # mostly filled/scanned
        # Reserved - qty done = qty to scan, we'll take the lower
        if len(suitable_lines) > 1:
            list_diff = suitable_lines.filtered(
                lambda x: x.qty_done - x.qty_reserved != 0).mapped(
                    lambda x: [x, x.qty_reserved - x.qty_done])
            res = min(list_diff, key=lambda x: x[1], default=[])
            suitable_lines = res[0] if res else suitable_lines[0]
        vals = {}
        if not suitable_lines:
            raise UserError(
                _('Be sure that you are scanning the same product'))
        vals['line_product_barcode'] = barcode
        vals['qty_done'] = suitable_lines.qty_done + 1
        suitable_lines.update(vals)
        if suitable_lines.qty_done > suitable_lines.qty_reserved:
            raise UserError(
                _("You cannot fill more than the requested quantity"))

    @api.multi
    def validate_product_set(self):
        self.ensure_one()
        for line in self.stock_barcode_product_line_ids.filtered(
                'line_product_barcode'):
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

    line_product_barcode = fields.Char()
    qty_reserved = fields.Float('Quantity Reserved')
    qty_done = fields.Float('Quantity Done')
    stock_barcode_product_id = fields.Many2one('stock.barcode.notracking')
    move_line_id = fields.Many2one('stock.move.line')
