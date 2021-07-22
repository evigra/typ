from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    map_location = fields.Text(
        string="Google Maps Location", help="Embeded url from google maps"
    )
    facebook_profile = fields.Char(
        string="Facebook URL", help="URL for the Facebook profile"
    )
    linkedin_profile = fields.Char(
        string="LinkedIn URL", help="URL for the LinkedIn profile"
    )
    upgradable = fields.Boolean(
        string="Category Can be Improved",
        help="""Mark this box if you want to allow the customer to upgrade"""
        """its category.""",
    )

    @api.model
    def _merge_partner(self, form_data):
        """Verify that a partner has the necessary validations to be upgraded
        to a new category. To do this, check that the mail does not belong to
        another user and that it is upgradeable. Once validated, the user
        information is updated with the data entered in the form.
        """
        email = form_data.get("email")
        p_found = self.search(
            [("email", "=", email), ("upgradable", "=", True)], limit=1
        )
        duplicate_partner = self.env["res.users"].search(
            [("login", "=", email), ("partner_id", "!=", p_found.id)]
        )
        if duplicate_partner:
            return {
                "error_title": _(
                    "This email already has upgraded " "or have portal access"
                ),
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
                "portal_id": self.env["res.groups"]
                .search([("is_portal", "=", True)], limit=1)
                .id,
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
        user_id = self.env["res.users"].search(
            [("partner_id", "=", p_found.id)]
        )
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

    @api.model
    def _get_my_quotations(self, limit=6):
        self.ensure_one()
        sale_order = self.env["sale.order"]
        domain = [
            (
                "message_partner_ids",
                "child_of",
                [self.commercial_partner_id.id],
            ),
            ("state", "in", ["sent", "cancel"]),
        ]
        return sale_order.search(domain, limit=limit)

    @api.model
    def _get_my_orders(self, limit=None):
        self.ensure_one()
        sale_order = self.env["sale.order"]
        domain = [
            (
                "message_partner_ids",
                "child_of",
                [self.commercial_partner_id.id],
            ),
            ("state", "in", ["sale", "done"]),
        ]
        return sale_order.search(domain, limit=limit)

    @api.model
    def _get_my_invoices(self, limit=None):
        self.ensure_one()
        acc_invoice = self.env["account.move"]
        domain = [
            ("type", "in", ["out_invoice", "out_refund"]),
            (
                "message_partner_ids",
                "child_of",
                [self.commercial_partner_id.id],
            ),
            ("state", "in", ["open", "paid", "cancel"]),
        ]
        return acc_invoice.search(domain, limit=limit)
