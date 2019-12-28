from odoo import api, models, _
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
            if (not lot and not picking_type.use_create_lots and
                    picking_type.use_existing_lots):
                raise UserError(_(
                    "Scanned number it's not a valid "
                    "Serial number for this product"))
        already_scanned = self.stock_barcode_lot_line_ids.filtered(
            lambda l: l.lot_name == barcode and l.qty_done > 0)
        if already_scanned and self.product_id.tracking == 'serial':
            raise UserError(_(
                'You cannot scan two times the same serial number'))

        already_exist = self.stock_barcode_lot_line_ids.filtered(
            lambda l: l.move_line_id.lot_id.name == barcode
            and l.qty_done == 0)

        suitable_line = self.stock_barcode_lot_line_ids.filtered(
            lambda l: not l.lot_name and l.qty_done == 0)
        if already_exist:
            suitable_line = already_exist
        if not suitable_line:
            raise UserError(
                _("You can't add more products than the reserved."))
        vals = {}
        vals['lot_name'] = barcode
        vals['qty_done'] = suitable_line[0].qty_done + 1
        suitable_line[0].update(vals)
        self.update({'qty_done': self.qty_done + 1})

    @api.model
    def default_get(self, fields):
        res = super(StockBarcodeLot, self).default_get(fields)
        if res.get('stock_barcode_lot_line_ids'):
            for values in res['stock_barcode_lot_line_ids']:
                values[2]['lot_name'] = values[2][
                    'lot_name'] if values[2]['qty_done'] > 0 else False
        return res

    def validate_lot(self):
        res = super(StockBarcodeLot, self).validate_lot()
        for line in self.stock_barcode_lot_line_ids:
            if line.move_line_id.lot_id:
                line.move_line_id.serial_id = line.move_line_id.lot_id
        return res
