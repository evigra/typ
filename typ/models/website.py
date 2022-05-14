from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_pricelist_available(self, req, show_visible=False):
        """If the current user can't see website prices, don't provide any pricelist"""
        if not self.env.user.has_group("typ.group_website_prices"):
            return self.env["product.pricelist"]
        return super()._get_pricelist_available(req, show_visible)
