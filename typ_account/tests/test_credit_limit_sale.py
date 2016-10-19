# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestCreditLimitSale(TransactionCase):

    def setUp(self):
        super(TestCreditLimitSale, self).setUp()
        self.sale_order = self.env['sale.order']
        self.product = self.env.ref('product.product_product_6')
        self.partner_1 = self.env['res.partner'].create({
            'name': 'Partner_1', 'credit_limit': 1000})
        self.warehouse_1 = self.env['stock.warehouse'].create({
            'name': 'Warehouse_1', 'code': 'WH1'})
        self.user_1 = self.env['res.users'].create({
            'name': 'User_1', 'login': 'user_1@test.com',
            'password': '123456'})
        self.journal = self.env.ref("account.bank_journal")
        self.account = self.env.ref("account.a_recv")
        self.payment_term_credit = self.env.ref(
            'account.account_payment_term_15days')
        # Create an invoice to have a pending payment
        dict_vals = {
            'partner_id': self.partner_1.id,
            'account_id': self.account.id,
            'payment_term': self.payment_term_credit.id,
            'journal_id': self.journal.id,
            'invoice_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'quantity': 1, 'price_unit': 500, })], }
        self.dict_vals_sale = {
            'partner_id': self.partner_1.id,
            'partner_invoice_id': self.partner_1.id,
            'partner_shipping_id': self.partner_1.id,
            'warehouse_id': self.warehouse_1.id,
            'order_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
                  'price_unit': 550, })], }
        self.account_invoice = self.env['account.invoice'].create(dict_vals)
        self.account_invoice.signal_workflow('invoice_open')
        # Create a sale team with invoice journal in journal_team_ids
        self.sale_team = self.env['crm.case.section'].create(
            {'name': 'Sale team test',
             'default_warehouse': self.warehouse_1.id,
             'journal_team_ids': [(4, self.journal.id)]})

    def test_00_credit_limit_sale_warning_message(self):
        """Test that message warning is raise when partner hasn't credit limit
        """
        sale_order = self.sale_order.create(self.dict_vals_sale)
        # Partner_1 has limit credit, no warning message must appears
        with_credit_limit = sale_order.get_partner_allowed_sale()
        self.assertNotIn('warning', with_credit_limit.keys())

    def test_002_credit_limit_sale_warning_message(self):
        """Test that message warning is raise when partner hasn't credit limit
        """
        sale_order = self.sale_order.create(self.dict_vals_sale)

        # Partner_1 hasn't limit credit
        self.partner_1.write({'credit_limit': 0.0})
        self.assertEqual(self.partner_1.credit_limit, 0.0)

        without_credit_limit = sale_order.get_partner_allowed_sale()
        self.assertIn('warning', without_credit_limit.keys())

    def test_10_credit_limit_sale_with_res_partner_warehouse_config(self):
        """Test that when partner has a res_partner_warehouse with the same
        warehouse that sale_order, the credit limit that is verified is that
        credit limit register in the res_partner_warehouse.
        """
        sale_order = self.sale_order.create(self.dict_vals_sale)

        # Create a res_partner_warehouse with enough credit limit
        res = self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_1.id, 'user_id': self.user_1.id,
            'credit_limit': 10000.00, 'partner_id': self.partner_1.id})
        self.assertEqual(self.partner_1.res_warehouse_ids, res)

        # Verifing credit limit in res_partner_warehouse created, partner_1
        # now has credit limit and message warning is not raise
        self.sale_team.write({'journal_team_ids': [(3, self.journal.id)]})
        with_credit_limit = sale_order.get_partner_allowed_sale()
        self.assertNotIn('warning', with_credit_limit.keys())
