# -*- coding: utf-8 -*-
from openerp import fields

from openerp.tests import common


class TestTypLandedCosts(common.TransactionCase):

    def setUp(self):
        super(TestTypLandedCosts, self).setUp()
        self.partner_1 = self.env.ref('base.res_partner_9')
        self.partner_2 = self.env.ref('base.res_partner_2')
        self.product_1 = self.env.ref(
            'stock_landed_costs_average.'
            'service_standard_periodic_landed_cost_1')
        self.product_2 = self.env.ref(
            'stock_landed_costs_average.'
            'service_standard_periodic_landed_cost_2')
        self.currency_1 = self.env.user.company_id.currency_id
        self.currency_2 = self.env.ref('base.USD')
        self.wizard_create_invoice = self.env['invoice.guides']
        self.journal = self.env.ref('account.check_journal')

    def create_guide(self, values=False, product=False):

        dict_vals = {
            'name': 'Test Guide',
            'date': fields.Date.today(),
            'partner_id': self.partner_1.id,
            'currency_id': self.currency_1.id,
            'journal_id': self.journal.id,
            'line_ids': [(0, 0,
                          {'product_id': product or self.product_1.id,
                           'cost': 100.00,
                           'freight_type': 'purchases'})]
        }
        dict_vals.update(values or {})
        return self.env['stock.landed.cost.guide'].create(dict_vals)

    def create_landed(self, values=False, cost_lines=False):

        dict_vals = {
            'account_journal_id': self.journal.id,
        }
        dict_vals.update(values or {})
        return self.env['stock.landed.cost'].create(dict_vals)
