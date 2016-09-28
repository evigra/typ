# coding: utf-8

from openerp.tests.common import TransactionCase


class TestLandedCost(TransactionCase):

    def setUp(self):
        super(TestLandedCost, self).setUp()
        self.stock_picking = self.env['stock.picking']
        self.transfer_obj = self.env['stock.transfer_details']
        self.partner = self.env.ref('base.res_partner_9')
        self.product = self.env.ref('product.product_product_6')
        self.picking_type = self.env.ref('stock.picking_type_in')

    def test_10_search_picking_landed_cost(self):
        """Search Source Document in field picking_ids for landed costs
        """
        demo_user = self.env.ref('base.user_demo')
        location_src = self.picking_type.default_location_src_id.id
        location_dest = self.picking_type.default_location_dest_id.id

        picking = self.stock_picking.sudo(demo_user).create({
            'partner_id': self.partner.id,
            'origin': '1234',
            'picking_type_id': self.picking_type.id,
            'move_lines': [
                (0, 0, {
                    'product_id': self.product.id,
                    'name': self.product.name,
                    'product_uom_qty': 5,
                    'product_uom': self.product.uom_id.id,
                    'price_unit': self.product.list_price,
                    'location_id': location_src,
                    'location_dest_id': location_dest,
                    })], })
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
        wizard_transfer_id.do_detailed_transfer()
        picking_origin = self.stock_picking.name_search(name=picking.origin)
        self.assertTrue(len(picking_origin) == 1, 'The picking no found')
        self.assertEquals(
            picking_origin[0][0], picking.id, 'The picking not match')
