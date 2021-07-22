from odoo import models, fields
from odoo.addons import decimal_precision as dp


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    initial_demand_qty = fields.Float(
        "Initial Demand",
        related="move_id.product_uom_qty",
        readonly=True,
        digits=dp.get_precision("Product Unit of Measure"),
        help="This is the quantity of products from an inventory "
        "point of view. For moves in the state 'done', this is the "
        "quantity of products that were actually moved. For other "
        "moves, this is the quantity of product that is planned to "
        "be moved. Lowering this quantity does not generate a "
        "backorder. Changing this quantity on assigned moves affects "
        "the product reservation, and should be done with care.",
    )
