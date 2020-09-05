
from .common import TestTypStock


class TestLandedCost(TestTypStock):

    def test_10_search_picking_landed_cost(self):
        """Search Source Document in field picking_ids for landed costs
        """
        demo_user = self.env.ref('base.user_demo')

        picking = self.create_picking_default(user=demo_user)
        picking.sudo(demo_user).action_confirm()
        picking.sudo(demo_user).force_assign()
        context = {
            'active_model': "stock.picking",
            'active_ids': [picking.id],
            'active_id': picking.id,
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": picking.id, }
            )
        for item in wizard_transfer_id.item_ids:
            item.quantity = item.expected_quantity
        wizard_transfer_id.do_detailed_transfer()
        picking_origin = self.stock_picking.name_search(name=picking.origin)
        self.assertTrue(len(picking_origin) == 1, 'The picking no found')
        self.assertEquals(
            picking_origin[0][0], picking.id, 'The picking not match')
