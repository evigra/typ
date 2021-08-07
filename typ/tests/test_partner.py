from odoo.tests import tagged

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
        # Set a pricelist and create partner
        self.env.user.sale_team_id = self.salesteam
        partner = self.env["res.partner"].create({"name": "To test Team Pricelist"})
        self.assertEqual(partner.property_product_pricelist, self.pricelist)

        # If user's sales team has no pricelist, the default one should be taken
        self.env.user.sale_team_id = False
        default_pricelist = self.env["ir.property"]._get("property_product_pricelist", "res.partner")
        partner = self.env["res.partner"].create({"name": "To test Native Pricelist"})
        self.assertEqual(partner.property_product_pricelist, default_pricelist)
        self.assertNotEqual(partner.property_product_pricelist, self.pricelist)
