from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.move.line'

    initial_demand_qty = fields.Float(
        'Initial Demand', related="move_id.product_uom_qty", readonly=True,
        digits=dp.get_precision('Product Unit of Measure'),
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")

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
