from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    partner_ids = fields.Many2many(
        "res.partner",
        "pricelist_section_rel",
        "partner_id",
        "pricelist_id",
        string="Pricelist's partner",
        help="Choose the Pricelist that partner can see",
    )

    def _get_partner_pricelist_multi(self, partner_ids, company_id=None):
        """Check for a pricelist in the user's sales team to use it by default"""
        pricelist_on_team = self.env.user.sale_team_id.sale_pricelist_id
        if pricelist_on_team:
            return {partner_id: pricelist_on_team for partner_id in partner_ids}
        return super()._get_partner_pricelist_multi(partner_ids, company_id=None)

    def get_product_price_rule_from_ui(self, product, quantity, partner):
        self.ensure_one()
        product = self.env["product.product"].browse(product)
        partner = self.env["res.partner"].browse(partner)
        return self._compute_price_rule([(product, quantity, partner)])
