from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_pricelist_available(self, req, show_visible=False):
        """If the current user is not logged in, don't provide any pricelist"""
        if self.env.user._is_public():
            return self.env["product.pricelist"]
        return super()._get_pricelist_available(req, show_visible)
