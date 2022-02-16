from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("partner")
class TestPartner(TypTransactionCase):
    def test_01_mail_loyalty(self):
        """Check that a loyalty email is sent when upgrading partner category"""
        self.customer.write(
            {
                "upgradable": True,
                "importance": "B",
            }
        )
        self.customer.write(
            {
                "upgradable": False,
                "importance": "A",
            }
        )
        self.assertIn(
            "/typ/static/img/email_loyalty_A.jpg",
            self.customer.message_ids[0].body,
        )

    def test_02_default_pricelist_salesteam(self):
        """When creating a partner, default pricelist should be taken from sales team"""
        # Create partner and check pricelist
        partner = self.env["res.partner"].create({"name": "To test Team Pricelist"})
        self.assertEqual(partner.property_product_pricelist, self.pricelist)

        # If user's sales team has no pricelist, the default one should be taken
        self.env.user.sale_team_id = False
        default_pricelist = self.env["product.pricelist"].search([("country_group_ids", "=", False)], limit=1)
        partner = self.env["res.partner"].create({"name": "To test Native Pricelist"})
        self.assertEqual(partner.property_product_pricelist, default_pricelist)
        self.assertNotEqual(partner.property_product_pricelist, self.pricelist)

    def test_03_credit_from_warehouses(self):
        """Check credit limit computation

        Credit limit should:
        - Be computed with the sum of credit limits available in all wharehouses
        - Be editable if there's no warehouse
        """
        # Credit limit should be 3000 (2000 + 1000)
        self.assertEqual(self.customer.credit_limit, 3000.0)
        self.assertEqual(
            self.customer.res_warehouse_ids.mapped("credit_limit"),
            [2000.0, 1000.0],
        )

        # If updating credit limit on one of the warehouse configs, partner's value should be recomputed
        self.customer.res_warehouse_ids[1].credit_limit = 500.0
        self.assertEqual(self.customer.credit_limit, 2500.0)

        # Credit limit should be readonly, as there are more than one warehouse config
        error_msg = "can't write on readonly field credit_limit"
        with Form(self.customer) as partner, self.assertRaisesRegex(AssertionError, error_msg):
            partner.credit_limit = 2200.0
