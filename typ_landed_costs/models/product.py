from odoo import models, fields


class ProductTemplate(models.Model):
    """class define attributes to product"""

    _inherit = "product.template"

    # TODO: It was spit_method in 11.0 then this need to be reviewed
    split_method_landed_cost = fields.Selection(default="by_current_cost_price")
