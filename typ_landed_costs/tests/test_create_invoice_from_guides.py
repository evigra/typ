# -*- coding: utf-8 -*-

from openerp.exceptions import ValidationError
from .common import TestTypLandedCosts


class TestCreateInvoiceFromGuides(TestTypLandedCosts):

    def test_00_guides_different_partners(self):
        """Test that raise a message when is try to create an invoice from
        guides with different partners
        """
        guide_1 = self.create_guide('Test Guide 1', self.partner_1,
                                    self.currency_1, self.product_1,
                                    self.journal)
        guide_2 = self.create_guide('Test Guide 2', self.partner_2,
                                    self.currency_1, self.product_2,
                                    self.journal)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        msg = ".*All guides selected must have the same partner.*"
        with self.assertRaisesRegexp(ValidationError, msg):
            self.wizard_create_invoice.with_context(context).create_invoice()

    def test_10_guides_different_currency(self):
        """Test that raise a message when is try to create an invoice from
        guides with different currency
        """
        guide_1 = self.create_guide('Test Guide 1', self.partner_1,
                                    self.currency_1, self.product_1,
                                    self.journal)
        guide_2 = self.create_guide('Test Guide 2', self.partner_1,
                                    self.currency_2, self.product_2,
                                    self.journal)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        msg = ".*All guides selected must have the same currency.*"
        with self.assertRaisesRegexp(ValidationError, msg):
            self.wizard_create_invoice.with_context(context).create_invoice()

    def test_20_invoice_guides_created(self):
        """Test create correctly an invoice when guides have the right
        configuration
        """
        guide_1 = self.create_guide('Test Guide 1', self.partner_1,
                                    self.currency_1, self.product_1,
                                    self.journal)
        guide_2 = self.create_guide('Test Guide 2', self.partner_1,
                                    self.currency_1, self.product_2,
                                    self.journal)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        res = self.wizard_create_invoice.with_context(context).create_invoice()
        self.assertIn('res_id', res)
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertEqual(len(invoice.invoice_line), 2)
        products = invoice.invoice_line.mapped('product_id')
        self.assertIn(self.product_1, products)
        self.assertIn(self.product_2, products)