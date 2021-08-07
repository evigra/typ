from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("sale")
class TestSale(TypTransactionCase):
    def test_01_sale_flow(self):
        sale_order = self.create_sale_order()

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
