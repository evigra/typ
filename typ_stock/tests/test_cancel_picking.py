from odoo.exceptions import Warning as UserError
from .common import TestTypStock


class TestCancelPicking(TestTypStock):
    def test_00_cancel_not_origin_picking(self):
        """Test that doesn't allowed cancel pickings with moves in transit
        location
        """
        self.dict_vals_line.update({"route_id": self.route_2.id})
        self.dict_vals.update(
            {
                "name": "Test cancel not origin picking",
                "warehouse_id": self.warehouse_2.id,
                "order_line": [(0, 0, self.dict_vals_line)],
            }
        )

        sale_order = self.env["sale.order"].create(self.dict_vals)
        sale_order.action_button_confirm()

        transit_pick = sale_order.picking_ids.filtered(lambda pick: pick.move_lines[0].location_id.usage == "transit")[
            0
        ]

        msg = "This picking cannot be cancelled."
        with self.assertRaisesRegexp(UserError, msg):
            transit_pick.action_cancel()

    def test_10_cancel_origin_picking(self):
        """Test that allowed cancel pickings without moves in transit locations"""
        self.dict_vals_line.update({"route_id": self.route_2.id})
        self.dict_vals.update(
            {
                "name": "Test cancel origin picking",
                "warehouse_id": self.warehouse_2.id,
                "order_line": [(0, 0, self.dict_vals_line)],
            }
        )

        sale_order = self.env["sale.order"].create(self.dict_vals)
        sale_order.action_button_confirm()

        origin_pick = sale_order.picking_ids.filtered(lambda pick: pick.move_lines[0].location_id.usage != "transit")[
            0
        ]

        origin_pick.action_cancel()
        self.assertTrue(origin_pick.state, "cancel")
