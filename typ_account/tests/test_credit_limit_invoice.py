# -*- coding: utf-8 -*-

from openerp import exceptions

from .common import TestTypAccount


class TestCreditLimitInvoice(TestTypAccount):

    def test_00_credit_limit_invoice_warning_message(self):
        """Warning must be shown when partner hasn't credit limit
        """
        self.account_invoice_1.action_invoice_open()
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)

        without_credit_lim = self.account_invoice_2._onchange_limit_credit()
        self.assertIn('warning', without_credit_lim.keys())

    def test_002_credit_limit_invoice_warning_message(self):
        """No warning message must appears because partner has credit limit
        """
        with_credit_limit = self.account_invoice_2._onchange_limit_credit()
        self.assertNotIn('warning', with_credit_limit.keys())

    def test_10_credit_limit_invoice_with_res_partner_warehouse_config(self):
        """Invoice can`t be validated when partner hasn't credit limit
        """
        self.conf_warehouse.write({'credit_limit': 0.0})
        self.assertEqual(self.conf_warehouse.credit_limit, 0.0)
        with self.assertRaises(exceptions.Warning):
            self.account_invoice_2.action_invoice_open()

    def test_20_credit_limit_invoice_with_res_partner_warehouse_config(self):
        """Invoice can be validated when partner hasn't credit limit`
        """
        self.account_invoice_2.action_invoice_open()
        self.assertEqual(self.account_invoice_2.state, 'open')
