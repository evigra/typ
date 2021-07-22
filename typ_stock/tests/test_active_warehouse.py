from odoo.exceptions import ValidationError
from .common import TestTypStock


class TestActiveWarehouse(TestTypStock):
    def test_00_warning_inactive_warehouse(self):
        """Test that ValidationError is raise when is try to inactive a
        warehouse with products on it"""
        warehouse = self.env.ref("stock.warehouse0")

        msg = (
            "You can not inactivate a warehouse with products on it, please"
            " adjust your inventories first and then come back and"
            " inactivate it."
        )
        with self.assertRaisesRegexp(ValidationError, msg):
            warehouse.active = False

    def test_10_inactive_and_active_warehouse(self):
        """Test that it can inactivate and then activate a warehouse without
        products on it"""
        warehouse = self.env.ref("typ_stock.whr_test_01")

        warehouse.active = False
        self.assertFalse(warehouse.active)
        warehouse.active = True
        self.assertTrue(warehouse.active)
