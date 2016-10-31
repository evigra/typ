# -*- coding: utf-8 -*-

from .common import TestTypLandedCosts


class TestGuides(TestTypLandedCosts):

    def test_00_validate_guide(self):
        """Test a guide can be validated and generate move lines"""
        # Guide starts in Draft state
        guide = self.create_guide()
        self.assertEqual(guide.state, 'draft')

        # Guide is validated correctly
        guide.action_valid()
        self.assertEqual(guide.state, 'valid')

        # Account Move generated with fields we expected
        move = guide.move_id
        self.assertEqual(move.journal_id, guide.journal_id)
        self.assertEqual(move.date, guide.date)
        self.assertEqual(move.company_id, guide.company_id)
        self.assertEqual(move.period_id, guide.period_id)

        # Move lines for credit and debit
        self.assertEqual(len(move.line_id), 2)

        # Move line for credit
        credit_line = guide.move_id.line_id.filtered(
            lambda line: line.credit > 0)
        cost = credit_line.guide_line_id.cost
        acc_stock_in = credit_line.guide_line_id.product_stock_account_in()
        self.assertEqual(credit_line.account_id.id, acc_stock_in)
        self.assertEqual(credit_line.debit, 0)
        self.assertEqual(credit_line.credit, cost)

        # Move line for debit
        debit_line = guide.move_id.line_id.filtered(
            lambda line: line.debit > 0)
        acc_expense = debit_line.product_id.categ_id.\
            property_account_expense_categ
        self.assertEqual(debit_line.account_id, acc_expense)
        self.assertEqual(debit_line.debit, cost)
        self.assertEqual(debit_line.credit, 0)

    def test_10_guide_multicurrency(self):
        """Guide with different currency creates the correct accounts moves"""
        # Create the guide with USD currency
        guide = self.create_guide({
            'currency_id': self.currency_2.id,
        })
        guide.action_valid()

        # Check if guide was created with the right currency
        self.assertEqual(guide.currency_id, self.currency_2)

        company_currency = guide.company_id.currency_id
        currency = self.currency_2

        # Move line for credit
        credit_line = guide.move_id.line_id.filtered(
            lambda line: line.credit > 0)
        # We get the cost marked in the Guide Line
        cost = credit_line.guide_line_id.cost
        # And compute it to the company currency
        comp_cost = currency.compute(cost, company_currency)
        self.assertEqual(credit_line.debit, 0)
        self.assertEqual(credit_line.credit, comp_cost)
        self.assertEqual(credit_line.amount_currency, cost * -1)
        self.assertEqual(credit_line.currency_id, currency)

        # Move line for debit
        debit_line = guide.move_id.line_id.filtered(
            lambda line: line.debit > 0)
        self.assertEqual(debit_line.debit, comp_cost)
        self.assertEqual(debit_line.credit, 0)
        self.assertEqual(debit_line.amount_currency, cost)

    def test_20_filter_journal_from_warehouse(self):
        """Test default warehouse from sale teams filters guide journals"""
        guide = self.create_guide()
        sale_team = self.env.ref('default_warehouse_from_sale_team'
                                 '.section_sales_default_team')
        guide.warehouse_id = sale_team.default_warehouse
        journal = self.env.ref('account.sales_journal')
        sale_team.write({'journal_team_ids': [(6, 0, journal.ids)]})
        res = guide.onchange_warehouse_id()
        self.assertIn('domain', res)
        dom = res['domain']
        self.assertIn('journal_id', dom)
        journal2 = self.env['account.journal'].search(dom['journal_id'])
        self.assertEqual(len(journal2), 1)
        self.assertIn(journal, journal2)
