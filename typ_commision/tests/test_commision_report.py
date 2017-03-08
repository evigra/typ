# -*- coding: utf-8 -*-

from openerp.tests.common import SingleTransactionCase


class TestCommisionReport(SingleTransactionCase):

    def setUp(self):
        super(TestCommisionReport, self).setUp()
        self.report = self.env.ref('typ_commision.report_base_01')
        self.invoice = self.env['account.invoice']
        self.invoice_line = self.env['account.invoice.line']

    def test_10_fill_all_fields(self):
        """Fill all new fields in account_invoice_line
        """
        inv_to_copy = self.invoice.search([('type', '=', 'out_invoice')],
                                          limit=1)
        inv_1 = inv_to_copy.copy()
        inv_1.payment_term.payment_type = 'cash'
        inv_1.signal_workflow('invoice_open')
        self.report.fill_required_fields()
        # Check the invoice lines
        lines = self.invoice_line.search(
            [('invoice_id.type', 'in', ('out_invoice', 'out_refund')),
             ('user_id', '=', False),
             ('state', 'in', ('open', 'paid')),
             ('invoice_id.user_id', '!=', False)]
        )
        # Check the result
        self.assertFalse(lines,
                         'The invoice lines were not updated')
        lines = self.invoice_line.search(
            [('type', 'in', ('out_invoice', 'out_refund'))], limit=20
        )
        for line in lines:
            line.refresh()
            inv = line.invoice_id
            val_line = (line.user_id, line.inv_name, line.currency)
            val_inv = (inv.user_id, inv.number, inv.currency_id)
            # Comparing values
            self.assertEqual(val_line, val_inv,
                             'The value between the invoice '
                             'and the lines are different')

    def test_20_fill_filtered_invoices(self):
        """Fill the lines that corresponding to the filter in the report
        """
        inv_to_copy = self.invoice.search([('type', '=', 'out_invoice')],
                                          limit=1)
        inv_1 = inv_to_copy.copy()
        inv_2 = inv_to_copy.copy()
        # Checking that the values are empty
        self.assertFalse(
            (inv_1.invoice_line.filtered(lambda a: a.user_id.id is not
                                         False) or
             inv_2.invoice_line.filtered(lambda a: a.user_id.id is not False)),
            'The invoices have values from the original invoice')
        # Validating Invoice
        inv_1.payment_term.payment_type = 'cash'
        inv_1.signal_workflow('invoice_open')
        # Fill the lines with filter
        self.report.fill_required_fields()
        lines = self.env['account.invoice.line'].search(
            [('invoice_id', '=', inv_1.id)])
        # Check that the new invoice is still empty
        self.assertFalse(
            inv_2.invoice_line.filtered(lambda a: a.user_id.id is not False),
            'The invoice was updated and this do not belong to the '
            'filter used')
        # Check that the new invoice lines were updated
        for line in lines:
            line.refresh()
            self.assertTrue(
                line.categ_id.id is not False,
                'The invoice line is not correctly set')
