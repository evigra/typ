from odoo import fields, models


class UserWishList(models.Model):
    _name = "user.wishlist"
    _description = "TODO: Once talk with the team describe it for v14.0"

    product_template_id = fields.Many2one("product.template", string="Product")
    qty = fields.Float(default=1)
    user_id = fields.Many2one("res.users", string="User")
