from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("sale")
class TestSale(TypTransactionCase):
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
