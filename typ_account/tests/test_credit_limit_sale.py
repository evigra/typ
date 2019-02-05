# -*- coding: utf-8 -*-

from openerp import exceptions

from .common import TestTypAccount


class TestCreditLimitSale(TestTypAccount):

    def test_00_credit_limit_sale_warning_message(self):
        """Message warning is not raise when partner has credit limit
        """
        with_credit_limit = self.sale_order.onchange_partner_id()
        self.assertFalse(with_credit_limit)

    def test_10_credit_limit_sale_cash_warning_message(self):
        """Message warning is not raise when partner hasn't credit limit but
        sale is cash
        """
        self.account_invoice_1.action_invoice_open()
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)

        self.dict_vals_sale.update(
            {'name': 'Sale test', 'type_payment_term': 'cash'})
        sale_order = self.sale_order_model.create(self.dict_vals_sale)
        with_credit_limit = sale_order.onchange_partner_id()
        self.assertFalse(with_credit_limit)

    def test_20_credit_limit_sale_warning_message(self):
        """Test that message warning is raise when partner hasn't credit limit
        """
        self.account_invoice_1.action_invoice_open()
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)

        without_credit_limit = self.sale_order.onchange_partner_id()
        self.assertIn('warning', without_credit_limit.keys())

    def test_30_credit_limit_sale_with_res_partner_warehouse_config(self):
        """Sale order can`t be confirmed when partner hasn't credit limit
        """
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_confirm()

    def test_40_credit_limit_sale_with_res_partner_warehouse_config(self):
        """Sale order can be confirmed when partner has credit limit
        """
        self.assertEqual(self.sale_order.state, 'draft')
        self.sale_order.action_confirm()
        self.assertEqual(self.sale_order.state, 'sale')

    def test_50_credit_limit_sale_without_res_partner_warehouse_config(self):
        """Sale order can`t be confirmed when doesn't exist a warehouse
        configuration for a warehouse selected.
        """
        self.dict_vals_sale.update({'warehouse_id': self.warehouse_2.id})
        warehouse_config = self.partner.res_warehouse_ids.filtered(
            lambda wh_conf: wh_conf.warehouse_id == self.warehouse_2)
        self.assertFalse(warehouse_config)
        self.sale_order = self.sale_order.create(self.dict_vals_sale)
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_confirm()

    def test_60_sale_when_allow_overdue_invoice_is_true(self):
        """Sale order can be confirmed when exist overdue payments but
        allow_overdue_invoice is true
        """
        self.dict_vals.update({'payment_term_id': self.payment_term_cash.id})
        account_invoice = self.account_invoice.create(self.dict_vals)
        account_invoice.action_invoice_open()
        self.dict_vals_sale.update({'name': 'Test001'})
        sale_order = self.sale_order.create(self.dict_vals_sale)
        self.assertEqual(sale_order.state, 'draft')
        with self.assertRaises(exceptions.Warning):
            self.sale_order.action_confirm()

        self.conf_warehouse.write({'allow_overdue_invoice': True})
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, 'sale')
