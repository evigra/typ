from odoo import fields
from odoo.tests import Form, HttpCase, TransactionCase
from odoo.tools.safe_eval import safe_eval


class TypCase:
    def setUp(self):
        super().setUp()
        self.user_admin = self.env.ref("base.user_admin")
        self.user_demo = self.env.ref("base.user_demo")
        self.uid = self.user_admin
        self.group_admin = self.env.ref("base.group_system")
        self.group_user = self.env.ref("base.group_user")
        self.group_validate_credit = self.env.ref("credit_management.allow_to_validate_credit_limit")
        self.customer = self.env.ref("base.res_partner_12")
        self.vendor = self.env.ref("base.res_partner_2")
        self.vendor2 = self.env.ref("base.res_partner_3")
        self.product = self.env.ref("product.product_product_16")
        self.product_cost = self.env.ref("typ.product_landing_cost")
        self.product_serial = self.env.ref("mrp.product_product_computer_desk")
        self.salesteam = self.env.ref("sales_team.crm_team_1")
        self.salesteam_europe = self.env.ref("sales_team.team_sales_department")
        self.fiscal_position_foreign = self.env.ref("l10n_mx.1_account_fiscal_position_foreign")
        self.pricelist = self.env.ref("website_sale.list_benelux")
        self.pricelist_christmas = self.env.ref("website_sale.list_christmas")
        self.pricelist_meta = self.env.ref("typ.pricelist_meta")
        self.company = self.env.ref("base.main_company")
        self.company_secondary = self.env.ref("stock.res_company_1")
        self.journal_expense = self.env["account.journal"].search([("name", "=", "Expense")], limit=1)
        self.journal_bills = self.env["account.journal"].search([("name", "=", "Vendor Bills")], limit=1)
        self.journal_guide = self.env.ref("typ.journal_cost_guide")
        self.warehouse_main = self.env.ref("stock.warehouse0")
        self.warehouse_test1 = self.env.ref("typ.whr_test_01")
        self.warehouse_test2 = self.env.ref("typ.whr_test_02")
        self.location_vendors = self.env.ref("stock.stock_location_suppliers")
        self.orderpoint = self.env.ref("typ.stock_warehouse_orderpoint_1")
        self.route_buy = self.env.ref("purchase_stock.route_warehouse0_buy")
        self.route_warehouse1_reception = self.env.ref("typ.whr_test_01_route_reception")
        self.pos_config = self.env.ref("point_of_sale.pos_config_main")
        self.usd = self.env.ref("base.USD")
        self.mxn = self.env.ref("base.MXN")
        self.today = fields.Date.context_today(self.company)

    def create_sale_order(self, partner=None, team=None, pricelist=None, **line_kwargs):
        if partner is None:
            partner = self.customer
        sale_order = Form(self.env["sale.order"].sudo())
        sale_order.partner_id = partner
        sale_order.stocksale = True
        if team is not None:
            sale_order.team_id = team
        if pricelist is not None:
            sale_order.pricelist_id = pricelist
            # Don't change price unless provided, as we presumably want it to be taken from pricelist
            line_kwargs.setdefault("price", False)
        sale_order = sale_order.save()
        self.create_so_line(sale_order, **line_kwargs)
        return sale_order

    def create_so_line(self, sale_order, product=None, quantity=1, price=100, vendor=None):
        if product is None:
            product = self.product
        with Form(sale_order) as so:
            with so.order_line.new() as line:
                line.product_id = product
                line.product_uom_qty = quantity
                if price is not False:
                    line.price_unit = price
                if vendor is not None:
                    line.route_id = self.route_buy
                    line.purchase_partner_id = vendor
                    self.fill_so_delivery_fields(so)

    def fill_so_delivery_fields(self, sale_order):
        sale_order.delivery_promise = self.today
        sale_order.shipping_to = "cliente"
        sale_order.partial_supply = "no"
        sale_order.type_of_import = "na"
        sale_order.shipping_by = "paquetexpress"
        sale_order.purchase_currency = sale_order.currency_id
        sale_order.special_discounts = "N/A"
        sale_order.notest = "A few notes"
        return sale_order

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

    def create_employee(self, name="John Doe", birthday=None):
        employee = Form(self.env["hr.employee"])
        employee.name = name
        employee.tz = self.env.user.tz
        if birthday:
            employee.birthday = birthday
        return employee.save()

    def assign_lots(self, move, lot_names):
        action_detailed_operation = move.action_show_details()
        move = move.with_context(action_detailed_operation["context"])
        with Form(move, view=action_detailed_operation["view_id"]) as mv:
            # Serial assignation will vary depending on wheter they need to be input as text or selected
            if move.env.context["show_lots_text"]:
                with mv.move_line_nosuggest_ids.new() as line:
                    line.lot_name = "\n".join(lot_names)
            else:
                for lot_name in lot_names[::-1]:
                    with mv.move_line_ids.new() as line:
                        line.lot_id = self._get_lot_from_name(line, lot_name)

    def _get_lot_from_name(self, line, lot_name):
        domain_str = line._view["fields"]["lot_id"]["domain"]
        domain = safe_eval(domain_str, line._values) + [("name", "=", lot_name)]
        lot = self.env["stock.production.lot"].search(domain, limit=1)
        self.assertTrue(lot, "lot not found for domain %s" % domain)
        return lot


class TypTransactionCase(TypCase, TransactionCase):
    pass


class TypHttpCase(TypCase, HttpCase):
    pass
