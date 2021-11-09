from odoo.tests import tagged

from .common import TypHttpCase


@tagged("post_install", "-at_install", "website")
class TestWebsite(TypHttpCase):
    def test_01_lead_from_product(self):
        """Create a lead from a website product by requesting a quotation"""
        self.start_tour(url_path="/shop", tour_name="lead_from_product_tour")

        # A lead should have been created linked to the selected product
        lead = self.env["crm.lead"].search([("name", "=", "Test subject")], limit=1, order="id desc")
        self.assertRecordValues(
            records=lead,
            expected_values=[
                {
                    "product_quotation_id": self.product.product_tmpl_id.id,
                    "contact_name": "John Doe",
                    "phone": "+52 55 1111 1111",
                    "email_from": "john@typ.mx",
                    "description": "Some description",
                },
            ],
        )
