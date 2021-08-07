import collections

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
    map_location = fields.Text(help="Embeded url from google maps")
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
        string="Warehouse configuration",
        help="Configurate salesman and credit limit to each warehouse",
    )

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

    @api.constrains("res_warehouse_ids")
    def unique_conf_partner_warehouse(self):
        for res in self:
            warehouse_ids = [res_wh.warehouse_id for res_wh in res.res_warehouse_ids]
            dict_values = dict(collections.Counter(warehouse_ids))
            for key in dict_values.keys():
                if dict_values[key] > 1:
                    raise ValidationError(
                        _(
                            "There is more than one configuration for warehouse %s. It must have only "
                            "one configuration for each warehouse",
                            key.name,
                        )
                    )

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
