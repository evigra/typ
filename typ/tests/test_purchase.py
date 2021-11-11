from odoo.tests import tagged

from .common import TypTransactionCase


@tagged("purchase")
class TestPurchase(TypTransactionCase):
    def test_01_purchase_serial(self):
        """Test purchasing and handling a product tracked by serial"""
        # Create and validate purchase order
        purchase_order = self.create_purchase_order(product=self.product_serial, quantity=2)
        purchase_order.button_confirm()
        self.assertRecordValues(
            records=purchase_order,
            expected_values=[
                {
                    "state": "purchase",
                    "picking_count": 1,
                    "report_lang": "en_US",
                },
            ],
        )

        # Receive products
        picking_po = purchase_order.picking_ids
        lot_names = ["SN1", "SN2"]
        self.assign_lots(picking_po.move_lines, lot_names)
        picking_po.button_validate()
        self.assertEqual(picking_po.state, "done")

        # Now sell the purchased products (same serials)
        sale_order = self.create_sale_order(product=self.product_serial, quantity=2)
        sale_order.action_confirm()
        self.assertEqual(sale_order.delivery_count, 1)

        # Delivery products to customer
        picking_so = sale_order.picking_ids
        self.assign_lots(picking_so.move_lines, lot_names)
        picking_so.button_validate()
        self.assertEqual(picking_so.state, "done")
