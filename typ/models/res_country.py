from odoo import fields, models


class Country(models.Model):
    _inherit = "res.country"

    city_ids = fields.One2many("res.city", "country_id", string="Cities")

    def get_website_sale_cities(self, state):
        return self.sudo().city_ids.filtered(
            lambda x: x.state_id and x.state_id.id == state
        )
