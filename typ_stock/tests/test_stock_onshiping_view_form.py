from .common import TestTypStock


class TestOpeninvoiceMethod(TestTypStock):
    def setUp(self):

        super().setUp()
        # get the objects
        self.wizard_onshipping = self.env["stock.invoice.onshipping"]
        self.journal_id = self.env.ref("account.sales_journal")

        # setting values to sale order
        self.dict_vals_line.update({"route_id": self.route_2.id})
        self.dict_vals.update(
            {
                "warehouse_id": self.warehouse_2.id,
                "order_line": [(0, 0, self.dict_vals_line)],
            }
        )

        sale_order = self.env["sale.order"].create(self.dict_vals)
        sale_order.action_button_confirm()

        self.transit_pick_id = sale_order.picking_ids.filtered(
            lambda pick: pick.move_lines[0].location_id.usage == "transit"
        ).mapped("id")
        self.transit_pick = sale_order.picking_ids.filtered(
            lambda pick: pick.move_lines[0].location_id.usage == "transit"
        )
        self.transit_pick.update({"invoice_state": "2binvoiced"})
        self.context = {"active_ids": self.transit_pick_id}

    # Methods of tests
    def test_00_onshipping_open_invoice_method(self):
        wizard = self.wizard_onshipping.with_context(self.context).create({"journal_id": self.journal_id.id})
        res = wizard.open_invoice()
        self.assertEqual(res["view_type"], "form")
