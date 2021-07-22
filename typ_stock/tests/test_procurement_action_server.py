from .common import TestTypStock


class TestProcurementActionServer(TestTypStock):
    def test_00_delete_purchase_order_line(self):
        """When remove the purchase order lines, their procurements must pass
        to state canceled
        """
        procurement = self.purchase_order.order_line.mapped("procurement_ids")
        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "running")

        self.purchase_order.order_line.unlink()

        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "cancel")

    def test_10_cancel_purchase_order(self):
        """When cancel purchase order, their procurements must pass to state
        canceled
        """
        procurement = self.purchase_order.order_line.mapped("procurement_ids")
        order_lines = procurement.mapped("purchase_line_id")

        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "running")

        self.purchase_order.action_cancel()
        self.assertTrue(self.purchase_order.state, "cancel")

        # Procurements must be canceled
        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "cancel")

        # Relation between procurements and purchase lines must be preserved
        order_lines_after_cancel = procurement.mapped("purchase_line_id")
        self.assertEqual(order_lines, order_lines_after_cancel)

        # product_qty and proce_unit values must not have changed
        self.assertEqual(order_lines.mapped("product_qty"), order_lines_after_cancel.mapped("product_qty"))
        self.assertEqual(order_lines.mapped("price_unit"), order_lines_after_cancel.mapped("price_unit"))

    def test_20_cancel_procurement(self):
        """When procurements are canceled, their purchase line related must
        be removed
        """
        procurement = self.purchase_order.order_line.mapped("procurement_ids")
        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "running")

        # Procurements must have a purchase line related
        self.assertTrue(procurement.mapped("purchase_line_id"))

        procurement.cancel()
        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "cancel")

        # Purchase lines related with the procurements canceled must be removed
        self.assertFalse(procurement.mapped("purchase_line_id"))

    def test_30_remove_purchese_order(self):
        """When purchase order is removed, their procurements must be
        canceled
        """
        procurement = self.purchase_order.order_line.mapped("procurement_ids")
        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "running")

        self.assertTrue(self.purchase_order.unlink())

        # Procurements must be canceled
        proc_state = list(set(procurement.mapped("state")))[0]
        self.assertEqual(proc_state, "cancel")
