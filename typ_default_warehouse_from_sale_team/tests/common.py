# -*- coding: utf-8 -*-

from openerp import fields
from openerp.tests import common


class TestTypSaleTeam(common.TransactionCase):

    def setUp(self):
        super(TestTypSaleTeam, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.warehouse = self.env.ref(
            'default_warehouse_from_sale_team.stock_warehouse_default_team')
        self.sale_team = self.env.ref(
            'default_warehouse_from_sale_team.section_sales_default_team')
        self.user = self.env.ref('base.user_root')
        self.journal_landed = self.env.ref("account.sales_journal")
        self.journal_landed_guide = self.env.ref(
            "account.refund_sales_journal")
        self.currency = self.env.user.company_id.currency_id

        self.landed_dict_vals = {
            'name': 'Test Landed',
            'date': fields.Date.today(),
        }
        self.guide_dict_vals = {
            'name': 'Test Guide',
            'date': fields.Date.today(),
            'partner_id': self.partner.id,
            'currency_id': self.currency.id,
        }
