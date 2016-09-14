# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase
from openerp import exceptions


class TestCreditLimitInvoice(TransactionCase):

    def setUp(self):
        super(TestCreditLimitInvoice, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.product = self.env.ref('product.product_product_6')
        self.partner_1 = self.env.ref('base.res_partner_9')
        self.partner_2 = self.env.ref('base.res_partner_13')
        self.journal = self.env.ref("account.bank_journal")
        self.account = self.env.ref("account.a_recv")
        self.payment_term_credit = self.env.ref(
            'account.account_payment_term_advance')

        self.partner_1.credit_limit = 200.00
        self.partner_2.credit_limit = 1000.00

        dict_vals = {
            'partner_id': self.partner_1.id,
            'account_id': self.account.id,
            'payment_term': self.payment_term_credit.id,
            'journal_id': self.journal.id,
            'invoice_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'quantity': 1, 'price_unit': 500, })], }
        self.account_invoice = self.account_invoice.create(dict_vals)

    def test_credit_limit_invoice_warning_message(self):
        # Partner_2 has limit credit, no warning message must appears
        with_credit_limit = self.account_invoice.onchange_partner_id(
            'out_invoice', self.partner_2.id)
        self.assertEqual(with_credit_limit.keys()[0], 'value')
        # Partner_1 hasn't limit credit
        without_credit_limit = self.account_invoice.onchange_partner_id(
            'out_invoice', self.partner_1.id)
        self.assertEqual(without_credit_limit.keys()[0], 'warning')

    def test_credit_limit_invoice_type_out_invoice(self):
        """This test validate invoices of type 'out_invoice'
        """
        with self.assertRaises(exceptions.Warning):
            self.account_invoice.signal_workflow('invoice_open')
