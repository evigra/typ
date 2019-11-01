from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.move.line'

    posx = fields.Char(
        'Corridor (X)',
        help="Optional product details, for information purpose only",
        compute='_compute_product_warehouse_id')

    posy = fields.Char(
        'Corridor (Y)',
        help="Optional product details, for information purpose only",
        compute='_compute_product_warehouse_id')

    posz = fields.Char(
        'Corridor (Z)',
        help="Optional product details, for information purpose only",
        compute='_compute_product_warehouse_id')

    @api.multi
    def _compute_product_warehouse_id(self):
        for line in self:
            product_warehouse_id = line.product_id.product_warehouse_ids.filtered(  # noqa
                lambda x:  x.warehouse_id == line.picking_id.warehouse_id)
            line.update({
                'posx': product_warehouse_id.posx,
                'posy': product_warehouse_id.posy,
                'posz': product_warehouse_id.posz,
            })
