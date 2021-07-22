from datetime import datetime
from .common import TestTypStock


class TestManualTransfer(TestTypStock):
    def test_10_make_transfer(self):

        demo_user = self.env.ref("base.user_demo")

        manual_transfer = (
            self.env["stock.manual_transfer"]
            .sudo(demo_user)
            .create(
                {
                    "warehouse_id": self.warehouse_2.id,
                    "date_planned": datetime.now(),
                    "route_id": self.route_3.id,
                    "transfer_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": self.product.id,
                                "product_uom_qty": 1.0,
                                "product_uom": self.product.uom_id.id,
                            },
                        )
                    ],
                }
            )
        )

        manual_transfer.sudo(demo_user).make_transfer()
        procurement_group_id = manual_transfer.procurement_group_id.id
        picking_ids = manual_transfer.env["stock.picking"].search([("group_id", "=", procurement_group_id)])
        self.assertTrue(len(picking_ids) == 2, "Pickings were not created correctly")
