# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestCreditLimitSale(TransactionCase):

    def setUp(self):
        super(TestCreditLimitSale, self).setUp()
        self.sale_order = self.env['sale.order']
        self.product = self.env.ref('product.product_product_6')
        self.partner_1 = self.env.ref('base.res_partner_9')
        self.partner_2 = self.env.ref('base.res_partner_13')

    def test_credit_limit_sale_warning_message(self):
        self.partner_1.credit_limit = 200.00
        self.partner_2.credit_limit = 1000.00

        dict_vals = {
            'partner_id': self.partner_2.id,
            'partner_invoice_id': self.partner_2.id,
            'partner_shipping_id': self.partner_2.id,
            'order_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
                  'price_unit': 500, })], }
        sale_order = self.sale_order.create(dict_vals)
        # Partner_2 has limit credit, no warning message must appears
        with_credit_limit = sale_order.onchange_partner_id(self.partner_2.id)
        self.assertEqual(with_credit_limit.keys()[0], 'value')
        # Partner_1 hasn't limit credit
        without_credit_limit = sale_order.onchange_partner_id(
            self.partner_1.id)
        self.assertEqual(without_credit_limit.keys()[0], 'warning')
