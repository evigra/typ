from odoo.tests import tagged

from .common import TypHttpCase


@tagged("post_install", "-at_install", "pos")
class TestPos(TypHttpCase):
    def setUp(self):
        super().setUp()
        # Make te "Table" product not trackeable to ease selecting it in the PoS
        self.product_serial.tracking = "none"

    def test_01_run_tours(self):
        """Run JavaScript tours"""
        self.pos_config.open_session_cb()

        # Check nested pricelists work correctly when product sin't in the 1st item
        self.start_tour(
            url_path="/pos/ui?config_id=%d" % self.pos_config.id,
            tour_name="pos_nested_pricelist",
            login=self.env.user.login,
        )

        # Create an order with partner, it should be automatically invoiced and posted
        self.start_tour(
            url_path="/pos/ui?config_id=%d" % self.pos_config.id,
            tour_name="pos_invoice_order",
            login=self.env.user.login,
        )
        pos_order = self.pos_config.current_session_id.order_ids[:1]
        self.assertEqual(pos_order.state, "invoiced")
        invoice = pos_order.account_move
        self.assertRecordValues(
            records=invoice,
            expected_values=[
                {
                    "partner_id": self.customer.id,
                    "invoice_payment_term_id": self.payment_term_immediate.id,
                    "state": "posted",
                    "pos_order_ids": pos_order.ids,
                    "invoice_origin": pos_order.name,
                    "amount_total": 348.0,
                    "amount_untaxed": 300.0,
                    "amount_tax": 48.0,
                },
            ],
        )
