from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _order = "posx asc, posy asc, posz asc, result_package_id desc, id"

    posx = fields.Char(
        "Aisle (X)",
        help="Optional product details, for information purpose only",
        compute="_compute_product_warehouse_id",
        store=True,
    )
    posy = fields.Char(
        "Shelves (Y)",
        help="Optional product details, for information purpose only",
        compute="_compute_product_warehouse_id",
        store=True,
    )
    posz = fields.Char(
        "Height (Z)",
        help="Optional product details, for information purpose only",
        compute="_compute_product_warehouse_id",
        store=True,
    )
    normalized_barcode = fields.Boolean(related="product_id.normalized_barcode")
    location_usage = fields.Selection(related="location_id.usage")

    @api.depends(
        "product_id",
        "product_id.product_warehouse_ids",
        "product_id.product_warehouse_ids.posx",
        "product_id.product_warehouse_ids.posy",
        "product_id.product_warehouse_ids.posz",
        "product_id.product_warehouse_ids.warehouse_id",
    )
    def _compute_product_warehouse_id(self):
        for line in self:
            product_warehouse_id = line.product_id.product_warehouse_ids.filtered(
                lambda x: x.warehouse_id == line.picking_id.warehouse_id
            )
            # Because there could be more than one ubication
            product_warehouse_id = product_warehouse_id[0] if product_warehouse_id else product_warehouse_id
            line.update(
                {
                    "posx": product_warehouse_id.posx,
                    "posy": product_warehouse_id.posy,
                    "posz": product_warehouse_id.posz,
                }
            )
