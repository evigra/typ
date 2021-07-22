from odoo.exceptions import Warning as UserError
from .common import TestTypStock


class TestStockInternal(TestTypStock):
    def test_10_validate_only_location_internal(self):
        """Validate pickings of internal type, allowing only internal movements
        between locations
        """
        demo_user = self.env.ref("base.user_demo")

        values = dict(
            picking_type_id=self.env.ref("stock.picking_type_internal").id,
        )

        lines = dict(
            location_dest_id=self.env.ref("stock.stock_location_customers").id,
        )

        picking = self.create_picking_default(
            extra_values=values,
            line=lines,
            user=demo_user,
        )
        picking.sudo(demo_user).action_confirm()
        picking.sudo(demo_user).force_assign()
        context = {
            "active_model": "stock.picking",
            "active_ids": [picking.id],
            "active_id": picking.id,
        }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {
                "picking_id": picking.id,
            }
        )

        msg = "Internal movements don't allow locations"
        with self.assertRaisesRegexp(UserError, msg):
            wizard_transfer_id.do_detailed_transfer()

    def test_20_validate_user_scrapped(self):
        """Validate pickings of internal type, allowing only confirm to users
        who are in manager / warehouse for location scrapped
        """
        demo_user = self.env.ref("base.user_demo")

        values = dict(
            picking_type_id=self.env.ref("stock.picking_type_internal").id,
        )

        lines = dict(
            location_id=self.env.ref("stock.stock_location_stock").id,
            location_dest_id=self.env.ref("typ_stock.location_scrapped_test").id,
        )

        picking = self.create_picking_default(
            extra_values=values,
            line=lines,
            user=demo_user,
        )

        picking.sudo(demo_user).action_confirm()

        msg = "Permission denied only manager/warehouse group"
        with self.assertRaisesRegexp(UserError, msg):
            picking.sudo(demo_user).action_assign()

    def test_30_validate_allow_move(self):
        """Validate pickings of internal type, allow inventory to internal"""
        demo_user = self.env.ref("base.user_demo")
        values = dict(
            picking_type_id=self.env.ref("stock.picking_type_internal").id,
        )

        lines = dict(
            location_id=self.env.ref("stock.location_inventory").id,
            location_dest_id=self.env.ref("stock.stock_location_stock").id,
        )
        picking = self.create_picking_default(
            extra_values=values,
            line=lines,
            user=demo_user,
        )
        picking.sudo(demo_user).action_confirm()
        picking.sudo(demo_user).force_assign()
        context = {
            "active_model": "stock.picking",
            "active_ids": [picking.id],
            "active_id": picking.id,
        }
        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {
                "picking_id": picking.id,
            }
        )
        wizard_transfer_id.do_detailed_transfer()
        self.assertEquals(wizard_transfer_id.picking_id.state, "done", "not Transfered")
