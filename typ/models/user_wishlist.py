# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class UserWishList(models.Model):
    _name = 'user.wishlist'

    product_template_id = fields.Many2one('product.template', string='Product')
    qty = fields.Float(default=1)
    user_id = fields.Many2one('res.users', string='User')
