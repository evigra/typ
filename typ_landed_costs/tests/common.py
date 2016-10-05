# -*- coding: utf-8 -*-

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
        self.currency_1 = self.env.ref('base.MXN')
        self.currency_2 = self.env.ref('base.USD')
        self.wizard_create_invoice = self.env['invoice.guides']
        self.journal = self.env.ref('account.check_journal')

    def create_guide(self, name, partner_id, currency_id, product_id,
                     journal_id):
        dict_vals = {
            'name': name,
            'partner_id': partner_id.id,
            'currency_id': currency_id.id,
            'journal_id': journal_id.id,
            'line_ids': [(0, 0,
                          {'product_id': product_id.id, 'cost': 100.00,
                           'freight_type': 'purchases'})]
        }
        return self.env['stock.landed.cost.guide'].create(dict_vals)
