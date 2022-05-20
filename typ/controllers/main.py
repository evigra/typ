from werkzeug.exceptions import Forbidden

from odoo import _, http, tools
from odoo.exceptions import ValidationError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteAccount(WebsiteSale):
    @http.route("/delete-address", type="json", auth="user", website=True)
    def delete_address(self, address_id):
        partner = request.env["res.partner"]
        logged_partner = request.env.user.partner_id
        shippings = partner.search(
            [
                ("id", "child_of", logged_partner.commercial_partner_id.ids),
                "|",
                ("type", "=", "delivery"),
                ("id", "=", logged_partner.commercial_partner_id.id),
            ]
        )
        for address in shippings:
            if address["id"] == int(address_id):
                address.unlink()
                return request.redirect("/my/account")

    @http.route(["/my/address"], type="http", auth="user", website=True)
    def my_address(self, **kw):
        values = self.checkout_values()
        values["active_page"] = "/my/address"
        return request.render("typ.account_address", values)

    @http.route(["/my/account/reset_password"], type="http", auth="user", website=True)
    def account_reset_pass(self, **kw):
        request.env.user.partner_id.signup_prepare(signup_type="reset")
        return request.redirect(request.env.user.partner_id.signup_url)

    def _get_mandatory_billing_fields(self):
        mbf = super()._get_mandatory_billing_fields()
        mbf.extend(["street2", "state_id"])
        # Required street removed from required list because it was replaced by
        # street_name, street_number and street_number2
        return mbf

    def _get_mandatory_shipping_fields(self):
        msf = super()._get_mandatory_shipping_fields()
        msf.extend(["street2", "state_id", "zip"])
        return msf

    @http.route()
    def shop(self, page=0, category=None, search="", ppg=False, **post):
        res = super().shop(page, category, search, ppg, **post)
        sort_by = post.get("order")
        res.qcontext["ppg"] = ppg
        res.qcontext["sort_by"] = sort_by
        return res

    @http.route("/shop/products/autocomplete", type="json", auth="public", website=True)
    def products_autocomplete(self, term, options=None, **kwargs):
        """Hide prices for users that can't see website prices when displaying suggestions for product searches"""
        options = options or {}
        if not request.env.user.has_group("typ.group_website_prices"):
            options["display_price"] = False
        return super().products_autocomplete(term, options, **kwargs)


class MyAccount(CustomerPortal):

    MANDATORY_BILLING_FIELDS = [
        "name",
        "phone",
        "email",
        "street",
        "street2",
        "city",
        "country_id",
    ]
    _items_per_page = 100

    @http.route(["/my/contact/edit"], type="http", auth="user", website=True)
    def contact_edit(self, redirect=None, **post):
        partner_obj = request.env["res.partner"].with_context(show_address=1).sudo()
        logged_partner = request.env.user.partner_id
        mode = (False, False)
        values = errors = {}
        # -1 When request comes from add user request
        partner_id = int(post.get("partner_id", -1))
        def_country_id = request.website.user_id.sudo().country_id
        # IF New contact
        if partner_id == -1:
            mode = ("new", "shipping")
        # IF VALID PARTNER
        else:
            if partner_id <= 0:
                return request.redirect("/my/address")
            partner = partner_obj.browse(partner_id)
            if partner_id == logged_partner.id:
                mode = ("edit", "billing")
            else:
                partner_shippings = logged_partner._get_partner_shippings()
                if partner_id in partner_shippings.mapped("id"):
                    mode = ("edit", "shipping")
                else:
                    return Forbidden()
            if mode:
                values = partner
        # IF POSTED
        if "submitted" in post:
            errors, error_msg = self._contact_details_validate(mode, post)
            if errors:
                errors["error_message"] = error_msg
                values = post
            else:
                contact_dict, errors, error_msg = self.values_postprocess(
                    logged_partner, mode, post, errors, error_msg
                )
                partner_id = self._contact_details_save(mode, contact_dict, post)
                if not errors:
                    return request.redirect("/my/address")

        country = (
            "country_id" in values
            and values["country_id"] != ""
            and request.env["res.country"].browse(int(values["country_id"]))
        )
        country = country and country.exists() or def_country_id
        render_values = {
            "partner_id": partner_id,
            "mode": mode,
            "checkout": values,
            "country": country,
            "countries": country.get_website_sale_countries(),
            "states": country.get_website_sale_states() if country else [],
            "error": errors,
            "active_page": "/my/address",
        }
        return request.render("typ.contact_edit", render_values)

    def _contact_details_validate(self, mode, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # data: values after preprocess
        error = {}
        error_message = []
        # Required fields from mandatory field function
        required_fields = (
            mode[1] == "shipping" and self._get_mandatory_shipping_fields() or self._get_mandatory_billing_fields()
        )
        # Check if state required
        if data.get("country_id"):
            country = request.env["res.country"].browse(int(data.get("country_id")))
            if "state_code" in country.get_address_fields() and country.state_ids:
                required_fields += ["state_id"]
        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = "missing"
        # email validation
        if data.get("email") and not tools.single_email_re.match(data.get("email")):
            error["email"] = "error"
            error_message.append(_("Invalid Email! Please enter a valid email address."))
        # vat validation
        partner = request.env["res.partner"]
        if data.get("vat") and hasattr(partner, "check_vat"):
            partner_dummy = partner.new(
                {
                    "vat": data["vat"],
                    "country_id": (int(data["country_id"]) if data.get("country_id") else False),
                }
            )
            try:
                partner_dummy.check_vat()
            except ValidationError:
                error["vat"] = "error"
        if [err for err in error.values() if err == "missing"]:
            error_message.append(_("Some required fields are empty."))
        return error, error_message

    def _contact_details_save(self, mode, checkout, all_values):
        partner_obj = request.env["res.partner"]
        if mode[0] == "new":
            partner_id = partner_obj.sudo().create(checkout)
        elif mode[0] == "edit":
            partner_id = int(all_values.get("partner_id", 0))
            if partner_id:
                partner = partner_obj.browse(partner_id)
                # double check
                shippings = partner._get_partner_shippings()
                if partner_id not in shippings.mapped("id") and partner_id != partner_id.id:
                    return Forbidden()
                partner_obj.browse(partner_id).sudo().write(checkout)
        return partner_id

    def _get_mandatory_shipping_fields(self):
        return WebsiteAccount()._get_mandatory_shipping_fields()

    def _get_mandatory_billing_fields(self):
        return WebsiteAccount()._get_mandatory_billing_fields()

    def values_postprocess(self, logged_partner, mode, values, errors, error_msg):
        values["country_id"] = int(values["country_id"])
        values["state_id"] = int(values["state_id"])
        new_values = {
            "customer_rank": 1,
            "team_id": (request.website.salesteam_id and request.website.salesteam_id.id),
        }
        lang = request.lang.code if request.lang.code in request.website.mapped("language_ids.code") else None
        if lang:
            new_values["lang"] = lang
        if mode == ("edit", "billing") and logged_partner.type == "contact":
            new_values["type"] = "other"
        if mode[1] == "shipping":
            new_values["parent_id"] = logged_partner.commercial_partner_id.id
            new_values["type"] = "delivery"
        new_values.update(values)
        new_values.pop("partner_id")
        new_values.pop("submitted")
        return new_values, errors, error_msg


class WebsiteLoyalty(http.Controller):
    @http.route(["/loyalty"], type="http", auth="public", website=True, sitemap=False)
    def create_partner(self, **post):
        category = post.get("category", False)
        values = {"category": category}
        if post.get("submitted", False):
            partner_obj = request.env["res.partner"].sudo()
            res = partner_obj._merge_partner(post)
            res["category"] = category
            if res.get("partner", False):
                return request.render("typ.loyalty_success", res)
            values = res
        return request.render("typ.loyalty", values)


class WebsiteContactUS(http.Controller):
    @http.route(["/contactus"], type="http", auth="public", website=True)
    def product_quotation(self, **post):
        product_tmpl_id = post.get("product", False)
        product_tmpl = request.env["product.template"].browse(int(product_tmpl_id))
        values = {
            "product_tmpl": product_tmpl,
        }
        return request.render("website.contactus", values)
