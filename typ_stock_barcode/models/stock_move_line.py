from collections import defaultdict

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.move.line'
    _order = 'typ_sort asc, result_package_id desc, id'

    typ_sort = fields.Integer("Typ Sorting")
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

    @api.multi
    @api.depends('product_id')
    def _compute_sorting(self):
        last_sort = self.search([
            ('typ_sort', '>', 0)],
            order="typ_sort desc", limit=1).typ_sort or 0
        moves = self.mapped('move_id')
        group_move = defaultdict(lambda: self.env['stock.move'])
        for smove in moves:
            complete_name = smove.product_id.categ_id.complete_name
            name_three = complete_name.rsplit("/", 3)
            if len(name_three) > 3:
                name_three.pop(0)
            # Discard category one
            name_three.pop()
            # Adjusted category up to level three and two
            complete_name_three = "/".join(name_three).strip()
            group_move[complete_name_three] |= smove

        # For each set of category
        for categ_moves in sorted(group_move.items()):
            # For each set of moves
            for smove in categ_moves[1].sorted(
                    key=lambda r: r.product_id.default_code):
                # For each line
                lines = smove.move_line_ids.sorted(
                    lambda x: x.location_id.id)
                for sort, line in enumerate(
                        lines, last_sort + 1 if last_sort else 1):
                    line.typ_sort = sort
                    last_sort = sort
