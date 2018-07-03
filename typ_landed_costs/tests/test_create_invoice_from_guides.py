# -*- coding: utf-8 -*-

from openerp.exceptions import ValidationError
from .common import TestTypLandedCosts


class TestCreateInvoiceFromGuides(TestTypLandedCosts):

    def test_00_guides_different_partners(self):
        """Test that raise a message when is try to create an invoice from
        guides with different partners
        """
        guide_1 = self.create_guide({'name': 'Test Guide 1'})
        guide_2 = self.create_guide({
            'name': 'Test Guide 2',
            'partner_id': self.partner_2.id,
        }, self.product_2.id)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        msg = ".*All guides selected must have the same partner.*"
        with self.assertRaisesRegexp(ValidationError, msg):
            self.wizard_create_invoice.with_context(context).create_invoice()

    def test_10_guides_different_currency(self):
        """Test that raise a message when is try to create an invoice from
        guides with different currency
        """
        guide_1 = self.create_guide({'name': 'Test Guide 1'})
        guide_2 = self.create_guide({
            'name': 'Test Guide 2',
            'currency_id': self.currency_2.id,
        }, self.product_2.id)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        msg = ".*All guides selected must have the same currency.*"
        with self.assertRaisesRegexp(ValidationError, msg):
            self.wizard_create_invoice.with_context(context).create_invoice()

    def test_20_invoice_guides_created(self):
        """Test create correctly an invoice when guides have the right
        configuration
        """
        guide_1 = self.create_guide({'name': 'Test Guide 1'})
        guide_2 = self.create_guide({'name': 'Test Guide 2'},
                                    self.product_2.id)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        res = self.wizard_create_invoice.with_context(context).create_invoice()
        self.assertIn('res_id', res)
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertEqual(len(invoice.invoice_line_ids), 2)
        products = invoice.invoice_line_ids.mapped('product_id')
        self.assertIn(self.product_1, products)
        self.assertIn(self.product_2, products)

    def test_30_try_invoice_guides_already_invoiced(self):
        """Test guides that already have been invoiced doesn't can be invoiced
        again
        """
        guide_1 = self.create_guide({'name': 'Test Guide 1'})
        guide_2 = self.create_guide({'name': 'Test Guide 2'},
                                    self.product_2.id)
        context = {'active_ids': [guide_1.id, guide_2.id],
                   'active_model': 'stock.landed.cost.guide'}
        res = self.wizard_create_invoice.with_context(context).create_invoice()
        self.assertIn('res_id', res)
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertTrue(guide_1.invoice_id, invoice)
        self.assertTrue(guide_2.invoice_id, invoice)
        self.assertTrue(guide_1.invoiced, True)
        self.assertTrue(guide_2.invoiced, True)
        msg = ".*is already invoiced.*"
        with self.assertRaisesRegexp(ValidationError, msg):
            self.wizard_create_invoice.with_context(context).create_invoice()
