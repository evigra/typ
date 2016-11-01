# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestSaleTypePaymentTerm(TransactionCase):

    def setUp(self):
        super(TestSaleTypePaymentTerm, self).setUp()
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.payment_term_cash = self.env.ref(
            'account.account_payment_term_immediate')
        self.partner = self.env['res.partner'].create({
            'name': 'Partner test',
            'property_payment_term': self.payment_term_credit.id})
        self.warehouse = self.env['stock.warehouse'].create({
            'name': 'Warehouse_1', 'code': 'WH1'})
        self.dict_sale = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'warehouse_id': self.warehouse.id,
            'type_payment_term': 'credit', }

    def test_00_type_payment_term_credit(self):
        """When type payment term is credit it must create the sale order
        with partner payment term
        """
        sale_order = self.env['sale.order'].create(self.dict_sale)
        sale_order.get_payment_term()
        self.assertTrue(sale_order.payment_term,
                        self.partner.property_payment_term)

    def test_10_type_payment_term_cash(self):
        """When type payment term is cash it must create the sale order
        with cash payment term
        """
        sale_order = self.env['sale.order'].create(self.dict_sale)
        sale_order.write({'type_payment_term': 'cash'})
        sale_order.get_payment_term()
        self.assertTrue(sale_order.payment_term, self.payment_term_cash)

    def test_20_type_payment_term_postdated_check(self):
        """When type payment term is postdated check it must create the sale
        order with cash payment term
        """
        sale_order = self.env['sale.order'].create(self.dict_sale)
        sale_order.write({'type_payment_term': 'postdated_check'})
        sale_order.get_payment_term()
        self.assertTrue(sale_order.payment_term, self.payment_term_cash)

    def test_30_type_payment_term_partner_without_payment_term(self):
        """When partner has not payment term, sale must be cash type
        automatically"""
        self.partner.write({'property_payment_term': False})
        sale_order = self.env['sale.order'].create(self.dict_sale)
        sale_order.get_payment_term()
        self.assertEqual(sale_order.type_payment_term, 'cash')

    def test_40_type_payment_term_partner_with_payment_term_cash(self):
        """When partner has payment term type cash, sale must be cash type
        automatically"""
        self.partner.write({'property_payment_term':
                            self.payment_term_cash.id})
        sale_order = self.env['sale.order'].create(self.dict_sale)
        sale_order.get_payment_term()
        self.assertEqual(sale_order.type_payment_term, 'cash')
