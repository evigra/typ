# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestTypePaymentTerm(TransactionCase):

    def setUp(self):
        super(TestTypePaymentTerm, self).setUp()
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.payment_term_cash = self.env.ref(
            'account.account_payment_term_immediate')
        self.partner = self.env['res.partner'].create({
            'name': 'Partner test',
            'property_payment_term': self.payment_term_credit.id})
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'Warehouse_1', 'code': 'WH1'})
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'warehouse_id': self.warehouse.id,
            'type_payment_term': 'credit', })

    def test_00_type_payment_term_credit(self):
        """When type payment term is credit it must create the sale order
        with partner payment term
        """
        self.sale_order.get_payment_term()
        self.assertTrue(self.sale_order.payment_term,
                        self.partner.property_payment_term)

    def test_10_type_payment_term_cash(self):
        """When type payment term is cash it must create the sale order
        with cash payment term
        """
        self.sale_order.write({'type_payment_term': 'cash'})
        self.sale_order.get_payment_term()
        self.assertTrue(self.sale_order.payment_term, self.payment_term_cash)

    def test_20_type_payment_term_postdated_check(self):
        """When type payment term is postdated check it must create the sale
        order with cash payment term
        """
        self.sale_order.write({'type_payment_term': 'postdated_check'})
        self.sale_order.get_payment_term()
        self.assertTrue(self.sale_order.payment_term, self.payment_term_cash)
