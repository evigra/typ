# -*- coding: utf-8 -*-<F3>eg

from openerp.exceptions import Warning as UserError
from openerp.tests.common import TransactionCase


class TestSaleBelowMargin(TransactionCase):

    def setUp(self):
        super(TestSaleBelowMargin, self).setUp()
        self.partner = self.env.ref('base.res_partner_9')
        self.product = self.env.ref('product.product_product_6')
        self.dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id, }
        self.dict_vals_line = {
            'name': self.product.name, 'product_id': self.product.id,
            'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
            'price_unit': 100, }
        self.demo_user = self.env.ref('base.user_demo')

    def test_00_sale_below_margin(self):
        """When sale order in create below margin minimum
        """
        self.dict_vals.update({'order_line': [(0, 0, self.dict_vals_line)]})
        msg = ".*You can not be sold below permitted margin.*"
        with self.assertRaisesRegexp(UserError, msg):
            self.env['sale.order'].sudo(self.demo_user).create(self.dict_vals)

    def test_01_sale_below_margin_with_price_zero(self):
        """When sale order in create with price unit set zero
        """
        self.dict_vals_line['price_unit'] = 0
        self.dict_vals.update({'order_line': [(0, 0, self.dict_vals_line)]})
        msg = ".*You can not be sold below permitted margin.*"
        with self.assertRaisesRegexp(UserError, msg):
            self.env['sale.order'].sudo(self.demo_user).create(self.dict_vals)
