from odoo.tests import common


class TestPointOfSaleCommon(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.pos_make_payment = self.env["pos.make.payment"]
        self.pos_order = self.env["pos.order"]
        self.pos_session = self.env["pos.session"]
        self.company_id = self.env.ref("base.main_company")
        self.product3 = self.env.ref("product.product_product_3")
        self.product4 = self.env.ref("product.product_product_4")
        self.partner1 = self.env.ref("base.res_partner_1")
        self.pos_config = self.env.ref("point_of_sale.pos_config_main")
        self.pricelist = self.env.ref("product.list0")
        self.pricelist.currency_id = self.company_id.currency_id

        # create a new session
        self.pos_order_session0 = self.pos_session.create({"user_id": 1, "config_id": self.pos_config.id})

        # create a new PoS order with 2 units of PC1 at 450 MXN
        # and 3 units of PCSC349 at 300  MXN.

        self.dict_vals = {
            "company_id": self.company_id.id,
            "partner_id": self.partner1.id,
            "pricelist_id": self.pricelist.id,
            "lines": [
                (
                    0,
                    0,
                    {
                        "name": "OL/0001",
                        "product_id": self.product3.id,
                        "price_unit": 450,
                        "qty": 2.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": "OL/0002",
                        "product_id": self.product4.id,
                        "price_unit": 300,
                        "qty": 3.0,
                    },
                ),
            ],
        }

        self.set_quantities_location(self.product3, 2.0)
        self.set_quantities_location(self.product4, 3.0)

    def set_quantities_location(self, product_id, qty):
        self.env["stock.quant"].create(
            {
                "location_id": self.pos_config.stock_location_id.id,
                "product_id": product_id.id,
                "quantity": qty,
            }
        )
