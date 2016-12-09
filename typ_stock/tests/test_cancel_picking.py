# coding: utf-8

from openerp.exceptions import Warning as UserError
from .common import TestTypStock


class TestCancelPicking(TestTypStock):

    def test_00_cancel_not_origin_picking(self):
        """Test that doesn't allowed cancel pickings that are not origin
        """
        self.dict_vals_line.update({'route_id': self.route_2.id})
        self.dict_vals.update({
            'warehouse_id': self.warehouse_2.id,
            'order_line': [(0, 0, self.dict_vals_line)], })

        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_button_confirm()

        not_origin_pick = sale_order.picking_ids.filtered(
            lambda pick: pick.move_lines[0].move_orig_ids.id is not False)[0]

        msg = ('This picking can not be cancel. Only origin picking can be '
               'cancel.')
        with self.assertRaisesRegexp(UserError, msg):
            not_origin_pick.action_cancel()

    def test_10_cancel_origin_picking(self):
        """Test that allowed cancel pickings that are origin
        """
        self.dict_vals_line.update({'route_id': self.route_2.id})
        self.dict_vals.update({
            'warehouse_id': self.warehouse_2.id,
            'order_line': [(0, 0, self.dict_vals_line)], })

        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_button_confirm()

        origin_pick = sale_order.picking_ids.filtered(
            lambda pick: pick.move_lines[0].move_orig_ids.id is False)[0]

        origin_pick.action_cancel()
        self.assertTrue(origin_pick.state, 'cancel')
