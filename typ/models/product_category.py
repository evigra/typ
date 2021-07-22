from odoo import models, fields


class ProductCategory(models.Model):

    _inherit = "product.category"

    allow_change_price_sale = fields.Boolean(
        help="Allow change price sale in the sale order for the stockable and "
        "consumable products attached to this category. The options doesn't "
        "apply to products attached to sub-categories of this category."
    )
