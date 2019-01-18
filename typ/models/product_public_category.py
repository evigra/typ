from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    landing_category = fields.Boolean(
        help="When selected this category will be displayed on the homepage")
    cover_img = fields.Binary(
        help="Contains the background-image of each category")
