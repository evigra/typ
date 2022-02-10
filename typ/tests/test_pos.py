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
