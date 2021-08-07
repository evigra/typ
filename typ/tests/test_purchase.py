from odoo.tests import tagged

from .common import TypTransactionCase


@tagged("purchase")
class TestPurchase(TypTransactionCase):
    def test_01_purchase_flow(self):
        purchase_order = self.create_purchase_order()
        purchase_order.button_confirm()
        self.assertEqual(purchase_order.state, "purchase")
