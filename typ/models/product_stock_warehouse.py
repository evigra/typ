from odoo import models, fields


class ProductStockWarehouse(models.Model):
    _name = "product.stock.warehouse"
    _description = "TODO: Once talk with the team describe it for v14.0"

    warehouse_id = fields.Many2one(
        "stock.warehouse", string="Warehouse", help="Set the warehouse"
    )
    posx = fields.Char(
        "Corridor (X)",
        help="Optional product details, for information purpose only",
    )
    posy = fields.Char(
        "Shelves (Y)",
        help="Optional product details, for information purpose only",
    )
    posz = fields.Char(
        "Height (Z)",
        help="Optional product details, for information purpose only",
    )
    product_id = fields.Many2one(
        "product.product", string="Product", help="Set the product"
    )
