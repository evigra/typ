from odoo import _, api, fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"

    pricelist_ids = fields.Many2many(
        "product.pricelist",
        "pricelist_section_rel",
        "pricelist_id",
        "partner_id",
        string="Pricelist's partner",
        help="Choose the Pricelist that partner can see",
    )
    buyer_id = fields.Many2one("res.users")
    map_location = fields.Text(help="Embedded url from google maps")
    facebook_profile = fields.Char(help="URL for the Facebook profile")
    linkedin_profile = fields.Char()
    upgradable = fields.Boolean(
        string="Category Can be Improved",
        help="Mark this box if you want to allow the customer to upgrade its category.",
    )
    importance = fields.Selection(
        selection=[
            ("AA", "AA"),
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("X", "X"),
            ("NEW", "NEW"),
            ("NEGOTIATION", "NEGOTIATION"),
            ("EMPLOYEE", "EMPLOYEE"),
            ("NOT CLASSIFIED", "NOT CLASSIFIED"),
        ],
    )
    potential_importance = fields.Selection(
        selection=[
            ("AA", "AA"),
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("X", "X"),
            ("NEW", "NEW"),
            ("NEGOTIATION", "NEGOTIATION"),
            ("EMPLOYEE", "EMPLOYEE"),
            ("NOT CLASSIFIED", "NOT CLASSIFIED"),
        ],
    )
    business_activity = fields.Selection(
        selection=[
            ("CONTRACTORS", "CON"),
            ("COMPANY", "COM"),
            ("WHOLESALERS", "WHO"),
            ("NOT CLASSIFIED", "NOT CLASSIFIED"),
            ("EMPLOYEE", "EMPLOYEE"),
            ("PUBLIC", "PUBLIC"),
        ],
        help="Not classified \nCON - Contractor\nCOM - Company\nWHO - Wholesaler",
    )
    partner_type = fields.Selection(
        selection=[
            ("OC", "OC - Operator contractor"),
            ("NC", "NC - New work contractor"),
            ("PC", "PC - Professional contractor"),
            ("RC", "RC - Refrigeration contractor"),
            ("ESP", "ESP - Specifier"),
            ("FSC", "FSC - Foodstuff company"),
            ("SUP", "SUP - Supermarket company"),
            ("BOT", "BOT - Bottler"),
            ("OTH", "OTH - Others"),
            ("WHC", "WHC - Wholesaler contractor"),
            ("WW", "WW - Wholesaler wholesaler"),
            ("WI", "WI - Wholesaler ironmonger"),
            ("DH", "DH - HVACR distributors"),
            ("NOT CLASSIFIED", "NOT CLASSIFIED"),
            ("EMPLOYEE", "EMPLOYEE"),
            ("PUBLIC", "PUBLIC"),
        ],
    )
    dealer = fields.Selection(
        selection=[
            ("PD", "PD - Premier dealer"),
            ("AD", "AD - Authorized dealer"),
            ("SD", "SD - Sporadic dealer"),
        ],
        string="Dealer type",
    )
    region = fields.Selection(
        selection=[
            ("NORTHWEST", "NORTHWEST"),
            ("WEST", "WEST"),
            ("CENTER", "CENTER"),
            ("NORTHEAST", "NORTHEAST"),
            ("SOUTHEAST", "SOUTHEAST"),
            ("SOUTH", "SOUTH"),
        ],
    )
    res_warehouse_ids = fields.One2many(
        comodel_name="res.partner.warehouse",
        inverse_name="partner_id",
        string="Warehouse configurations",
        help="Configurate salesperson and credit limit to each warehouse.",
    )
    # Unless credit management, credit limit is not company dependent but warehouse dependent.
    # The computed value is the sum of credit available in all warehouses and editable only if
    # there aren't more than one warehouse configured
    credit_limit = fields.Float(
        company_dependent=False,
        store=True,
        compute="_compute_credit_limit",
        inverse="_inverse_credit_limit",
    )
    res_warehouse_count = fields.Integer(
        string="# Warehouse Configurations",
        compute="_compute_res_warehouse_count",
    )

    @api.depends("res_warehouse_ids.credit_limit")
    def _compute_credit_limit(self):
        partner_warehouses = self.env["res.partner.warehouse"].read_group(
            domain=[("partner_id", "in", self.ids)],
            fields=["partner_id", "credit_limit"],
            groupby=["partner_id"],
        )
        credits_by_partner = {w["partner_id"][0]: w["credit_limit"] for w in partner_warehouses}
        for partner in self:
            partner.credit_limit = credits_by_partner.get(partner.id, 0.0)

    def _inverse_credit_limit(self):
        partners_single_warehouse = self.filtered(lambda p: len(p.res_warehouse_ids) == 1)
        for partner in partners_single_warehouse:
            partner.res_warehouse_ids[0].credit_limit = partner.credit_limit

    @api.depends("res_warehouse_ids")
    def _compute_res_warehouse_count(self):
        for partner in self:
            partner.res_warehouse_count = len(partner.res_warehouse_ids)

    def write(self, vals):
        upgradable_before = self.filtered("upgradable")
        res = super().write(vals)
        non_upgradable_after = self - self.filtered("upgradable")
        (upgradable_before & non_upgradable_after)._send_loyalty_email()
        return res

    def _send_loyalty_email(self):
        loyalties_to_email = ["A", "AA"]
        for partner in self.filtered(lambda p: p.importance in loyalties_to_email):
            partner.message_post_with_view(
                "typ.message_partner_loyalty",
                subtype_id=self.env.ref("mail.mt_note").id,
                partner_ids=[(6, 0, partner.ids)],
            )

    def _get_credit_amount(self):
        """Consider warehouse when computing credit limit"""
        warehouse_id = self.env.context.get("credit_limit_warehouse_id")
        if not warehouse_id:
            return super()._get_credit_amount()
        partner = self.commercial_partner_id
        partner_warehouse = self.env["res.partner.warehouse"].search(
            [
                ("partner_id", "=", partner.id),
                ("warehouse_id", "=", warehouse_id),
            ],
            limit=1,
        )
        return partner_warehouse.credit_limit

    def _get_total_due(self):
        """Consider journal when filtering unreconciled journal items to compute due amount"""
        journal_id = self.env.context.get("credit_limit_journal_id")
        if not journal_id:
            return super()._get_total_due()
        unreconciled_aml_domain = self._fields["unreconciled_aml_ids"].domain.copy()
        unreconciled_aml_domain += [
            ("partner_id", "=", self.commercial_partner_id.id),
            ("journal_id", "=", journal_id),
        ]
        unreconciled_amls = self.env["account.move.line"].read_group(
            domain=unreconciled_aml_domain,
            fields=["partner_id", "amount_residual"],
            groupby=["partner_id"],
        )
        return unreconciled_amls[0]["amount_residual"] if unreconciled_amls else 0.0

    def _get_so_lines_domain_to_check_credit_limit(self):
        """Consider warehouse when retrieving sale order lines on which amount for credit will be computed"""
        domain = super()._get_so_lines_domain_to_check_credit_limit()
        warehouse_id = self.env.context.get("credit_limit_warehouse_id")
        if warehouse_id:
            domain = expression.AND([domain, [("warehouse_id", "=", warehouse_id)]])
        return domain

    @api.model
    def _merge_partner(self, form_data):
        """Verify that a partner has the necessary validations to be upgraded to a new category.
        To do this, check that the mail does not belong to another user and that it is upgradeable.
        Once validated, the user information is updated with the data entered in the form.
        """
        email = form_data.get("email")
        p_found = self.search([("email", "=", email), ("upgradable", "=", True)], limit=1)
        duplicate_partner = self.env["res.users"].search([("login", "=", email), ("partner_id", "!=", p_found.id)])
        if duplicate_partner:
            return {
                "error_title": _("This email already has upgraded " "or have portal access"),
                "error": _("please contact us if you think this is a mistake"),
            }
        if not p_found:
            return {
                "error_title": _("You are not elegible for upgrade"),
                "error": _("please contact us if you think this is a mistake"),
            }
        pw = self.env["portal.wizard"]
        cpw = self.env["change.password.wizard"]
        categs = {
            "titanium": "AA",
            "black": "A",
        }
        # update values in the partner record
        category = form_data.get("category")
        values = {
            "name": form_data.get("name"),
            "street_name": form_data.get("street_name"),
            "street_number": form_data.get("street_number"),
            "street_number2": form_data.get("street_number2"),
            "zip": form_data.get("zip"),
            "street2": form_data.get("l10n_mx_edi_colony"),
            "l10n_mx_edi_colony": form_data.get("l10n_mx_edi_colony"),
            "facebook_profile": form_data.get("facebook_profile"),
            "linkedin_profile": form_data.get("linkedin_profile"),
            "upgradable": False,
            "importance": categs.get(category, False),
        }
        p_found.write(values)
        # give portal access
        portal_wizard = pw.create(
            {
                "portal_id": self.env["res.groups"].search([("is_portal", "=", True)], limit=1).id,
                "user_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": p_found.id,
                            "email": p_found.email,
                            "in_portal": True,
                        },
                    )
                ],
            }
        )
        portal_wizard.action_apply()
        user_id = self.env["res.users"].search([("partner_id", "=", p_found.id)])
        # set new password to freshly created res.user
        reset_pwd_wizard = cpw.create(
            {
                "user_ids": [
                    (
                        0,
                        0,
                        {
                            "user_id": user_id.id,
                            "user_login": user_id.email,
                            "new_passwd": form_data.get("password"),
                        },
                    )
                ],
            }
        )
        reset_pwd_wizard.change_password_button()
        return {"partner": p_found, "category": category}

    @api.model
    def _get_partner_shippings(self):
        self.ensure_one()
        shippings = self.search(
            [
                ("id", "child_of", self.commercial_partner_id.ids),
                "|",
                ("type", "=", "delivery"),
                ("id", "=", self.commercial_partner_id.id),
            ],
            order="id desc",
        )
        return shippings

    def _inverse_product_pricelist(self):
        """Allow to set an empty pricelist on the partner

        By default, when trying to clear a partner's pricelist (the property), Odoo does
        nothing [1]. This means, once the property is set, it's only possible to change
        it but not clearing it.

        Clearing a pricelist is a valid case for us, because, for some partners, we want the
        pricelist to be taken from the sales team, which is not possible if there's one set in the
        partner, as the latter would have priority.

        [1] https://github.com/odoo/odoo/blob/475e6b3cb027/addons/product/models/res_partner.py#L34
        """
        partners_with_pricelist = self.filtered("property_product_pricelist")
        res = super(ResPartner, partners_with_pricelist)._inverse_product_pricelist()
        partners_wo_pricelist = self - partners_with_pricelist
        self.env["ir.property"]._set_multi(
            name="property_product_pricelist",
            model=self._name,
            values={partner.id: False for partner in partners_wo_pricelist},
        )
        return res
