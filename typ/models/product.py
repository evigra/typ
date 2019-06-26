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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # TODO: Check if this does not cause performance problems since at update
    # process will update this fields when updating product, stock and typ
    # modules Ticket 6289
    description = fields.Text(
        translate=True,
        help="A precise description of the Product, used only for internal "
        "information purposes.")
    description_purchase = fields.Text(
        'Purchase Description', translate=True,
        help="A description of the Product that you want to communicate "
        "to your vendors. This description will be copied to every "
        "Purchase Order, Receipt and Vendor Bill/Credit Note.")
    description_sale = fields.Text(
        'Sale Description', translate=True,
        help="A description of the Product that you want to communicate to "
        "your customers. This description will be copied to every Sales Order,"
        " Delivery Order and Customer Invoice/Credit Note")
    description_picking = fields.Text(
        'Description on Picking', translate=True)
    description_pickingout = fields.Text(
        'Description on Delivery Orders', translate=True)
    description_pickingin = fields.Text(
        'Description on Receptions', translate=True)

    route_ids = fields.Many2many(
        'stock.location.route', 'stock_route_product_product', 'product_id',
        'route_id', 'Routes', domain="[('product_selectable', '=', True)]",
        help="Depending on the modules installed, this will allow you to "
        "define the route of the product: whether it will be bought, "
        "manufactured, MTO/MTS,...")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=80):
        res = super(ProductProduct, self).name_search(
            name, args=args, operator=operator, limit=limit)
        if not limit or len(res) >= limit:
            limit = (limit - len(res)) if limit else False
        if (not name or len(res) >= limit):
            return res
        limit -= len(res)
        products = self.search(
            [('attribute_value_ids.name', operator, name)], limit=limit)
        if not products:
            return res
        res.extend(products.name_get())
        return res
