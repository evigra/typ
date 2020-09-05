
from openerp import models, fields


class ProductTemplate(models.Model):
    """class define attributes to product"""
    _inherit = "product.template"

    split_method = fields.Selection(default="by_current_cost_price")
