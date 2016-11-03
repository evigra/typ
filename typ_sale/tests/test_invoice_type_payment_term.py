# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestInvoiceTypePaymentTerm(TransactionCase):

    def setUp(self):
        super(TestInvoiceTypePaymentTerm, self).setUp()
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.payment_term_cash = self.env.ref(
            'account.account_payment_term_immediate')
        self.partner = self.env['res.partner'].create({
            'name': 'Partner test',
            'property_payment_term': self.payment_term_credit.id})
        self.product = self.env.ref('product.product_product_6')
        self.journal = self.env.ref("account.sales_journal")
        self.account = self.env.ref("account.a_recv")
        self.dict_vals = {
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'journal_id': self.journal.id,
            'invoice_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'quantity': 1, 'price_unit': 500, })], }

    def test_00_invoice_type_payment_term_credit(self):
        """When type payment term is credit it must create the invoice
        with partner payment term
        """
        invoice = self.env['account.invoice'].create(self.dict_vals)
        invoice.get_payment_term()
        self.assertTrue(invoice.payment_term,
                        self.partner.property_payment_term)

    def test_10_invoice_type_payment_term_cash(self):
        """When type payment term is cash it must create the invoice
        with cash payment term
        """
        invoice = self.env['account.invoice'].create(self.dict_vals)
        invoice.write({'type_payment_term': 'cash'})
        invoice.get_payment_term()
        self.assertTrue(invoice.payment_term, self.payment_term_cash)

    def test_20_invoice_type_payment_term_postdated_check(self):
        """When type payment term is postdated check it must create the invoice
        with cash payment term
        """
        invoice = self.env['account.invoice'].create(self.dict_vals)
        invoice.write({'type_payment_term': 'postdated_check'})
        invoice.get_payment_term()
        self.assertTrue(invoice.payment_term, self.payment_term_cash)

    def test_30_invoice_type_payment_term_partner_without_payment_term(self):
        """When partner has not payment term, invoice must be cash type
        automatically"""
        self.partner.write({'property_payment_term': False})
        invoice = self.env['account.invoice'].create(self.dict_vals)
        invoice.get_payment_term()
        self.assertEqual(invoice.type_payment_term, 'cash')

    def test_40_invoice_type_payment_term_partner_with_payment_term_cash(self):
        """When partner has payment term type cash, invoice must be cash type
        automatically"""
        self.partner.write({'property_payment_term':
                            self.payment_term_cash.id})
        invoice = self.env['account.invoice'].create(self.dict_vals)
        invoice.get_payment_term()
        self.assertEqual(invoice.type_payment_term, 'cash')