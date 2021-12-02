from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    _order = "sequence asc, applied_on, min_quantity desc, categ_id desc, id desc"

    sequence = fields.Integer(default=5)
