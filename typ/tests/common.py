from odoo import fields
from odoo.tests import Form, HttpCase, TransactionCase


class TypCase:
    def setUp(self):
        super().setUp()
        self.user_admin = self.env.ref("base.user_admin")
        self.user_demo = self.env.ref("base.user_demo")
        self.uid = self.user_admin
        self.group_admin = self.env.ref("base.group_system")
        self.group_user = self.env.ref("base.group_user")
        self.customer = self.env.ref("base.res_partner_12")
        self.vendor = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_16")
        self.product_cost = self.env.ref("typ.product_landing_cost")
        self.salesteam = self.env.ref("sales_team.crm_team_1")
        self.pricelist = self.env.ref("website_sale.list_benelux")
        self.pricelist_christmas = self.env.ref("website_sale.list_christmas")
        self.company = self.env.ref("base.main_company")
        self.company_secondary = self.env.ref("stock.res_company_1")
        self.journal_expense = self.env["account.journal"].search([("name", "=", "Expense")], limit=1)
        self.journal_bills = self.env["account.journal"].search([("name", "=", "Vendor Bills")], limit=1)
        self.journal_guide = self.env.ref("typ.journal_cost_guide")
        self.warehouse_test1 = self.env.ref("typ.whr_test_01")
        self.usd = self.env.ref("base.USD")
        self.mxn = self.env.ref("base.MXN")
        self.today = fields.Date.context_today(self.company)

    def create_sale_order(self, partner=None, team=None, **line_kwargs):
        if partner is None:
            partner = self.customer
        sale_order = Form(self.env["sale.order"])
        sale_order.partner_id = partner
        sale_order.stocksale = True
        if team is not None:
            sale_order.team_id = team
        sale_order = sale_order.save()
        self.create_so_line(sale_order, **line_kwargs)
        return sale_order

    def create_so_line(self, sale_order, product=None, quantity=1, price=100):
        if product is None:
            product = self.product
        with Form(sale_order) as so:
            with so.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = quantity
                line.price_unit = price

    def create_purchase_order(self, partner=None, shipment_date=None, **line_kwargs):
        if partner is None:
            partner = self.vendor
        if shipment_date is None:
            shipment_date = self.today
        purchase_order = Form(self.env["purchase.order"])
        purchase_order.partner_id = partner
        purchase_order.shipment_date = shipment_date
        purchase_order = purchase_order.save()
        self.create_po_line(purchase_order, **line_kwargs)
        return purchase_order

    def create_po_line(self, purchase_order, product=None, quantity=1, price=50):
        if product is None:
            product = self.product
        with Form(purchase_order) as po:
            with po.order_line.new() as line:
                line.product_id = product
                line.product_qty = quantity
                line.price_unit = price


class TypTransactionCase(TypCase, TransactionCase):
    pass


class TypHttpCase(TypCase, HttpCase):
    pass
