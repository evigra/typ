from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    _order = "sequence asc"

    sequence = fields.Integer(default=5)
