from odoo import api, fields, models


class CrmCaseSection(models.Model):

    _inherit = "crm.team"

    journal_guide_id = fields.Many2one(
        "account.journal",
        "Journal landed cost guide",
        help="It indicates journal to be used when landed cost guide is" " created",
    )
    journal_landed_id = fields.Many2one(
        "account.journal", "Journal landed cost", help="It indicates journal to be used when landed cost is created"
    )
    sale_pricelist_id = fields.Many2one(
        "product.pricelist",
        "Default sale pricelist",
        help="It indicates the sale pricelist" " to be used when partner is created",
    )


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
        """Retrieve the applicable pricelist for given partners in a given,
        company. Check for a default pricelist in the user sale team to use it
        in partner by default.

            :param company_id: if passed, used for looking up properties,
                instead of current user's company
            :return: a dict {partner_id: pricelist}
        """
        partner = self.env["res.partner"]
        prop = self.env["ir.property"].with_context(force_company=company_id or self.env.user.company_id.id)
        res = super()._get_partner_pricelist_multi(partner_ids, company_id=None)

        # retrieve values of property
        result = prop.get_multi("property_product_pricelist", partner._name, partner_ids)
        remaining_partner_ids = [pid for pid, val in result.items() if not val]
        sale_team = self.env.user.sale_team_id
        pricelist_id = sale_team and sale_team.sale_pricelist_id
        if remaining_partner_ids and pricelist_id:
            for pid in remaining_partner_ids:
                result[pid] = pricelist_id
            return result
        return res


class ResPartner(models.Model):

    _inherit = "res.partner"

    @api.model
    def _get_sale_pricelist_id(self):
        sale_team = self.env.user.sale_team_id
        return sale_team and sale_team.sale_pricelist_id.id

    pricelist_ids = fields.Many2many(
        "product.pricelist",
        "pricelist_section_rel",
        "pricelist_id",
        "partner_id",
        string="Pricelist's partner",
        help="Choose the Pricelist that partner can see",
    )
    buyer_id = fields.Many2one("res.users", "Buyer", index=True)

    @api.model
    def default_get(self, field):
        """Overwrite default_get method to set the pricelist for the new
        partner depending of the user's salesteam which is trying to create
        the partner
        """
        res = super().default_get(field)
        res.update(
            {
                "property_product_pricelist": self._get_sale_pricelist_id() or None,
            }
        )
        return res

    @api.depends("user_ids.groups_id")
    def _compute_is_employee(self):
        for partner in self:
            partner_id = self.env["res.users"].search([("partner_id", "=", partner.id), ("share", "=", False)])
            if partner_id:
                partner.is_employee = partner_id.has_group("base.group_user")

    is_employee = fields.Boolean(
        compute="_compute_is_employee",
        string="Is Employee?",
        readonly=True,
        store=True,
        help="If user belongs to employee group return True",
    )
