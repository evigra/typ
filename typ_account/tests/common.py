# -*- coding: utf-8 -*-

from openerp.tests import common


class TestTypAccount(common.TransactionCase):

    def setUp(self):
        super(TestTypAccount, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.sale_order = self.env['sale.order']
        self.product = self.env.ref('product.product_product_6')
        self.partner = self.env.ref('typ_account.partner_01')
        self.warehouse = self.env.ref('typ_account.wh_01')
        self.sale_team = self.env.ref('typ_account.sale_team_01')
        self.journal = self.env.ref("account.sales_journal")
        self.account = self.env.ref("account.a_recv")
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.conf_warehouse = self.env.ref('typ_account.res_partner_wh_01')

        # Create an invoice to have a pending payment
        dict_vals = {
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'payment_term': self.payment_term_credit.id,
            'journal_id': self.journal.id,
            'invoice_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'quantity': 1, 'price_unit': 500, })], }
        self.account_invoice_1 = self.account_invoice.create(dict_vals)
        self.account_invoice_1.signal_workflow('invoice_open')
        self.account_invoice_2 = self.account_invoice.create(dict_vals)

        self.dict_vals_sale = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'warehouse_id': self.warehouse.id,
            'order_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
                  'price_unit': 500, })], }
        self.sale_order = self.sale_order.create(self.dict_vals_sale)
