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

    def test_02_address_creation_edit_remove(self):
        """Create a new address, edit it and remove it from the website"""
        # Creation of the new address
        self.start_tour(url_path="/my/address", tour_name="address_creation_tour", login="admin")

        address = self.env["res.partner"].search([("name", "=", "John Doe")], limit=1, order="id desc")
        self.assertRecordValues(
            records=address,
            expected_values=[
                {
                    "parent_id": self.user_admin.partner_id.id,
                    "name": "John Doe",
                    "phone": "+52 55 1111 1111",
                    "street": "Morelos",
                    "street2": "Some neighborhood",
                    "zip": "20020",
                    "country_id": self.mx_country.id,
                    "state_id": self.mx_aguascalientes.id,
                    "city": "Aguascalientes",
                }
            ],
        )

        # Record values "Phone" and "Neighborhood" edited
        self.start_tour(url_path="/my/address", tour_name="address_edit_tour", login="admin")

        self.assertRecordValues(
            records=address,
            expected_values=[
                {
                    "parent_id": self.user_admin.partner_id.id,
                    "name": "John Doe",
                    "phone": "+52 55 2222 2222",
                    "street": "Morelos",
                    "street2": "Another neighborhood",
                    "zip": "20020",
                    "country_id": self.mx_country.id,
                    "state_id": self.mx_aguascalientes.id,
                    "city": "Aguascalientes",
                }
            ],
        )

        # Remove address
        self.start_tour(url_path="/my/address", tour_name="address_remove_tour", login="admin")

        self.assertFalse(address.exists())
