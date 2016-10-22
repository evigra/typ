# -*- coding: utf-8 -*-

from openerp import exceptions

from .common import TestTypAccount


class TestCreditLimitSale(TestTypAccount):

    def test_00_credit_limit_sale_warning_message(self):
        """Message warning is not raise when partner has credit limit
        """
        with_credit_limit = self.sale_order.get_partner_allowed_sale()
        self.assertNotIn('warning', with_credit_limit.keys())

    def test_002_credit_limit_sale_warning_message(self):
        """Test that message warning is raise when partner hasn't credit limit
        """
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)

        without_credit_limit = self.sale_order.get_partner_allowed_sale()
        self.assertIn('warning', without_credit_limit.keys())

    def test_10_credit_limit_sale_with_res_partner_warehouse_config(self):
        """Sale order can`t be confirmed when partner hasn't credit limit
        """
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)
        with self.assertRaises(exceptions.Warning):
            self.sale_order.signal_workflow("order_confirm")

    def test_20_credit_limit_sale_with_res_partner_warehouse_config(self):
        """Sale order can be confirmed when partner has credit limit
        """
        self.assertEqual(self.sale_order.state, 'draft')
        self.sale_order.signal_workflow("order_confirm")
        self.assertIn(self.sale_order.state, ('manual', 'progress'))
