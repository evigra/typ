
from .common import TestTypStock


class TestPropagateTransfer(TestTypStock):

    def test_10_transfer_all_pickings(self):
        """Propagate transfer of all pickings
        """
        self.first_pick.move_lines[0].move_dest_id.rule_id.write(
            {'propagate_transfer': True})
        self.first_pick.move_lines[0].move_dest_id.move_dest_id.rule_id.write(
            {'propagate_transfer': True})

        self.wizard_transfer_id.do_detailed_transfer()

        # 3 pickings it must have passed to done state
        list_states = [picking.state for picking in
                       self.sale_order.picking_ids]
        self.assertEqual(list_states.count('done'), 3)

    def test_20_transfer_two_pickings(self):
        """Propagate transfer only to the second picking
        """
        self.first_pick.move_lines[0].move_dest_id.rule_id.write(
            {'propagate_transfer': True})

        self.wizard_transfer_id.do_detailed_transfer()

        # 2 pickings it must have passed to done state
        list_states = [picking.state for picking in
                       self.sale_order.picking_ids]
        self.assertEqual(list_states.count('done'), 2)
        self.assertEqual(list_states.count('assigned'), 1)

    def test_30_transfer_partial_pickings(self):
        """Propagate transfer only to the second picking but transfering
        the first picking partially
        """
        self.first_pick.move_lines[0].move_dest_id.rule_id.write(
            {'propagate_transfer': True})

        self.wizard_transfer_id.item_ids[0].write({'quantity': 1})
        self.wizard_transfer_id.do_detailed_transfer()

        # It must has created 2 pickings more, in total it has been 5 pickings
        self.assertEqual(len(self.sale_order.picking_ids), 5)
        list_states = [picking.state for picking in
                       self.sale_order.picking_ids]
        self.assertEqual(list_states.count('done'), 2)
        self.assertEqual(list_states.count('assigned'), 1)
        self.assertEqual(list_states.count('waiting'), 1)
        self.assertEqual(list_states.count('partially_available'), 1)
