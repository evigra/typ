# coding: utf-8
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    is_highlight = fields.Boolean(default=False, string='Highlight Product',
                                  help="Manual selector for featured products")

    @api.model
    def _get_price_taxed(self, untaxed_price):
        self.ensure_one()
        taxes = []
        for tax in self.taxes_id:
            taxes += tax.sudo().compute_all(
                untaxed_price, currency=None, quantity=1.0,
                product=self, partner=None).get('taxes')
        taxed_price = sum([tax.get('amount') for tax in taxes]) + untaxed_price
        return taxed_price

    @api.multi
    def is_favorite(self):
        self.ensure_one()
        result_wish = self.env['user.wishlist'].search(
            [('product_template_id', '=', self.id),
             ('user_id', '=', self.env.uid)], limit=1)
        return bool(result_wish)
