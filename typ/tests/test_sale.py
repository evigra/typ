from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("sale")
class TestSale(TypTransactionCase):
    def create_invoices_from_sale_orders(self, sale_orders):
        ctx = {
            "active_model": sale_orders._name,
            "active_ids": sale_orders.ids,
            "active_id": sale_orders[0].id,
            "open_invoices": True,
        }
        wizard = self.env["sale.advance.payment.inv"].with_context(**ctx).create({})
        wizard_res = wizard.create_invoices()
        invoices = self.env[wizard_res["res_model"]].browse(wizard_res["res_id"])
        return invoices

    def test_01_sale_flow(self):
        sale_order = self.create_sale_order()
        self.assertRecordValues(
            records=sale_order,
            expected_values=[
                {
                    "state": "draft",
                    # Pricelist set on the partner
                    "pricelist_id": self.pricelist_christmas.id,
                    "fiscal_position_id": False,
                }
            ],
        )

        # We shouldn't be able to edit partner once the SO has lines
        error_msg = "You can't change Partner in Sales Orders with lines."
        with self.assertRaisesRegex(ValidationError, error_msg):
            sale_order.partner_id = False

        # Only members of the group to edit sales price should be hable to do it
        group_edit_price = self.env.ref("typ.res_group_modify_price_sale")
        self.env.user.groups_id -= group_edit_price
        error_msg = "You can not modify the sales price of product"
        with Form(sale_order) as so, so.order_line.edit(0) as sol:
            with self.assertRaisesRegex(ValidationError, error_msg):
                sol.price_unit += 10
            self.env.user.groups_id |= group_edit_price
            sol.price_unit += 10

        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")

    def test_02_pricelist_from_salesteam(self):
        """When the selected customer has no pricelist, it should be taken from the salesteam"""
        self.customer.property_product_pricelist = False
        sale_order = self.create_sale_order()
        self.assertEqual(sale_order.pricelist_id, self.pricelist)

    def test_03_fiscal_position_salesteam(self):
        """Fiscal position should always be taken from the sales team, not from the partner"""
        customer_fiscal_position = self.env["account.fiscal.position"].create(
            {
                "name": "Customer Position",
            }
        )
        self.customer.property_account_position_id = customer_fiscal_position
        sale_order = self.create_sale_order(team=self.salesteam_europe)
        self.assertEqual(sale_order.fiscal_position_id, self.fiscal_position_foreign)

    def test_04_special_so(self):
        """Test creation a special sale order, i.e. an SO that creates a purchase order with a specific vendor"""
        # Create an SO with two lines using two different vendors
        sale_order = self.create_sale_order(vendor=self.vendor, quantity=5)
        self.create_so_line(sale_order, vendor=self.vendor2, quantity=3)
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")

        # There should be two new purchase orders, one per vendor
        purchase_orders = self.env["purchase.order"].search(
            [
                ("create_date", ">=", sale_order.create_date),
            ],
            order="id",
        )
        self.assertRecordValues(
            records=purchase_orders,
            expected_values=[
                {
                    "partner_id": self.vendor.id,
                    "currency_id": self.mxn.id,
                    "origin": self.orderpoint.name,
                    "picking_type_id": self.warehouse_test1.in_type_id.id,
                },
                {
                    "partner_id": self.vendor2.id,
                    "currency_id": self.mxn.id,
                    "origin": self.orderpoint.name,
                    "picking_type_id": self.warehouse_test1.in_type_id.id,
                },
            ],
        )
        self.assertRecordValues(
            records=purchase_orders.order_line,
            expected_values=[
                {
                    "order_id": purchase_orders[0].id,
                    "product_id": self.product.id,
                    "product_qty": 5.0,
                    "price_unit": 25.0,
                    "orderpoint_id": self.orderpoint.id,
                },
                {
                    "order_id": purchase_orders[1].id,
                    "product_id": self.product.id,
                    "product_qty": 3.0,
                    "price_unit": 20.0,
                    "orderpoint_id": self.orderpoint.id,
                },
            ],
        )

    def test_05_credit_limit(self):
        """Test the multi-warehouse credit limit feature for sales"""
        self.env.user.groups_id -= self.group_validate_credit

        # Global credit limit is 3000, but only 2000 for the current warehouse.
        # If using 2500, it should fail
        sale_order = self.create_sale_order(price=2500)
        error_msg = "has exceeded the credit limit. Credit available to use is %s"
        with self.assertRaisesRegex(UserError, error_msg % "2,000.00"):
            sale_order.action_confirm()

        # In 2nd warehouse, it should be 1000
        with Form(sale_order) as so:
            so.warehouse_id = self.warehouse_test2
        with self.assertRaisesRegex(UserError, error_msg % "1,000.00"):
            sale_order.action_confirm()

        # But if using 1500 in 1st warehouse, it should succeed
        sale_order = self.create_sale_order(price=1500)
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")

        # Create invoice from order
        invoice = self.create_invoices_from_sale_orders(sale_order)
        self.assertRecordValues(
            records=invoice,
            expected_values=[
                {
                    "invoice_origin": sale_order.name,
                    "state": "draft",
                    "amount_untaxed": 1500.0,
                },
            ],
        )

        # Try to invoice 2500, it should fail as did the sale order
        with Form(invoice) as inv, inv.invoice_line_ids.edit(0) as inv_line:
            inv_line.price_unit = 2500.0
        invoice.action_post()
        self.assertEqual(invoice.state, "draft")
        self.assertIn(error_msg % 2000.0, invoice.message_ids[0].body)

        # If going back to invoice 1500, it should succeed
        with Form(invoice) as inv, inv.invoice_line_ids.edit(0) as inv_line:
            inv_line.price_unit = 1500.0
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")
