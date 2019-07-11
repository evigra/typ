# coding: utf-8
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import division
from werkzeug.exceptions import Forbidden

from odoo import http, tools, _
from odoo.http import request, Controller
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.sale.controllers.portal import CustomerPortal as SP
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import ValidationError


class WebsiteAccount(WebsiteSale):

    @http.route('/delete-address', type='json',
                auth='user', website=True)
    def delete_address(self, address_id):
        partner = request.env['res.partner']
        logued_partner = request.env.user.partner_id
        shippings = partner.search([
            ("id", "child_of", logued_partner.commercial_partner_id.ids),
            '|', ("type", "=", "delivery"),
            ("id", "=", logued_partner.commercial_partner_id.id)
        ])
        for address in shippings:
            if address['id'] == int(address_id):
                address.unlink()
                return request.redirect('/my/account')

    @http.route(['/my/orders-record'], type='http', auth="user", website=True)
    def my_orders_record(self, **kw):
        values = self.checkout_values()
        values['active_page'] = '/my/orders-record'
        return request.render("typ.my-orders", values)

    @http.route(['/my/address'], type='http', auth="user", website=True)
    def my_address(self, **kw):
        values = self.checkout_values()
        values['active_page'] = '/my/address'
        return request.render("typ.account_address", values)

    @http.route(['/my/account/reset_password'],
                type='http', auth="user", website=True)
    def account_reset_pass(self, **kw):
        request.env.user.partner_id.signup_prepare(signup_type="reset")
        return request.redirect(request.env.user.partner_id.signup_url)

    def _get_mandatory_billing_fields(self):
        mbf = super(WebsiteAccount, self)._get_mandatory_billing_fields()
        mbf.extend(
            ['street2', 'state_id'])
        # Required street removed from required list because it was replaced by
        # street_name, street_number and street_number2
        return mbf

    def _get_mandatory_shipping_fields(self):
        msf = super(WebsiteAccount, self)._get_mandatory_shipping_fields()
        msf.extend(
            ['street2', 'state_id', 'zip'])
        return msf

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteAccount, self).shop(page,
                                               category,
                                               search,
                                               ppg,
                                               **post)
        sort_by = post.get('order')
        res.qcontext['ppg'] = ppg
        res.qcontext['sort_by'] = sort_by
        return res


class MyAccountInvoices(PortalAccount):
    @http.route()
    def portal_my_invoices(self, *arg, **kw):
        response = super(MyAccountInvoices, self).portal_my_invoices(*arg,
                                                                     **kw)

        response.qcontext['in_view'] = "invoices"

        status_filter = kw.get('invoices_status')
        response.qcontext['invoices_status'] = status_filter

        month_filter = kw.get('month')
        response.qcontext['month_filter'] = month_filter

        invoices = response.qcontext.get('invoices')

        if status_filter == 'open':
            my_invoices = invoices.filtered(lambda rec:
                                            rec.state == 'open' and
                                            rec.type == 'out_invoice')
            response.qcontext.update({'invoices': my_invoices})
        elif status_filter == 'paid':
            my_invoices = invoices.filtered(lambda rec:
                                            rec.state == 'paid' and
                                            rec.type == 'out_invoice')
            response.qcontext.update({'invoices': my_invoices})
        else:
            my_invoices = invoices.filtered(lambda rec:
                                            rec.type == 'out_invoice')
            response.qcontext.update({'invoices': my_invoices})

        total_unpaid_usd = my_invoices.filtered(
            lambda rec: rec.currency_id.name == 'USD'
            ).mapped('residual')
        sum_unpaid_usd = sum(total_unpaid_usd)
        response.qcontext['total_unpaid_usd'] = sum_unpaid_usd

        total_unpaid_mxn = my_invoices.filtered(
            lambda rec: rec.currency_id.name == 'MXN'
            ).mapped('residual')
        sum_unpaid_mxn = sum(total_unpaid_mxn)
        response.qcontext['total_unpaid_mxn'] = sum_unpaid_mxn

        amount_usd = my_invoices.filtered(
            lambda rec: rec.currency_id.name == 'USD'
            and rec.state != 'cancel'
            ).mapped('amount_total')
        to_paid_usd = sum(amount_usd) - sum_unpaid_usd
        response.qcontext['total_to_paid_usd'] = to_paid_usd

        amount_mxn = my_invoices.filtered(
            lambda rec: rec.currency_id.name == 'MXN'
            and rec.state != 'cancel'
            ).mapped('amount_total')
        to_paid_mxn = sum(amount_mxn) - sum_unpaid_mxn
        response.qcontext['total_to_paid_mxn'] = to_paid_mxn

        return response

    @http.route(['/my/credit_notes'], type='http', auth="user", website=True)
    def my_credit_notes(self, *arg, **kw):
        response = super(MyAccountInvoices, self).portal_my_invoices(*arg,
                                                                     **kw)

        response.qcontext['in_view'] = "credit_notes"

        status_filter = kw.get('invoices_status')
        response.qcontext['invoices_status'] = status_filter

        month_filter = kw.get('month')
        response.qcontext['month_filter'] = month_filter

        invoices = response.qcontext.get('invoices')

        if status_filter == 'open':
            my_credit_notes = invoices.filtered(lambda rec:
                                                rec.state == 'open' and
                                                rec.type == 'out_refund')
            response.qcontext.update({'invoices': my_credit_notes})
        elif status_filter == 'paid':
            my_credit_notes = invoices.filtered(lambda rec:
                                                rec.state == 'paid' and
                                                rec.type == 'out_refund')
            response.qcontext.update({'invoices': my_credit_notes})
        else:
            my_credit_notes = invoices.filtered(lambda rec:
                                                rec.type == 'out_refund')
            response.qcontext.update({'invoices': my_credit_notes})

        response.qcontext.update({'default_url': '/my/credit_notes'})

        total_unpaid_usd = my_credit_notes.filtered(
            lambda rec: rec.currency_id.name == 'USD'
            ).mapped('residual')
        sum_unpaid_usd = sum(total_unpaid_usd)
        response.qcontext['total_unpaid_usd'] = sum_unpaid_usd

        total_unpaid_mxn = my_credit_notes.filtered(
            lambda rec: rec.currency_id.name == 'MXN'
            ).mapped('residual')
        sum_unpaid_mxn = sum(total_unpaid_mxn)
        response.qcontext['total_unpaid_mxn'] = sum_unpaid_mxn

        amount_usd = my_credit_notes.filtered(
            lambda rec: rec.currency_id.name == 'USD'
            ).mapped('amount_total')
        to_paid_usd = sum(amount_usd) - sum_unpaid_usd
        response.qcontext['total_to_paid_usd'] = to_paid_usd

        amount_mxn = my_credit_notes.filtered(
            lambda rec: rec.currency_id.name == 'MXN'
            ).mapped('amount_total')
        to_paid_mxn = sum(amount_mxn) - sum_unpaid_mxn
        response.qcontext['total_to_paid_mxn'] = to_paid_mxn

        return request.render("typ.my_invoices", response.qcontext)

    @http.route(['/my/payment_complements'], type='http',
                auth="user", website=True)
    def my_payment_complements(self, **kw):
        partner = request.env.user.partner_id.ids
        account_payments = request.env['account.payment']

        complements = account_payments.sudo().search([(
            'partner_id', '=', partner), ('state', '=', 'reconciled')])

        values = {
            'payment_partner': complements,
        }

        return request.render("typ.payment_complements", values)


class MyAccountOrders(SP):
    @http.route()
    def portal_my_orders(self, *arg, **kw):
        response = super(MyAccountOrders, self).portal_my_orders(*arg, **kw)
        orders = response.qcontext.get('orders')

        month_filter = kw.get('month')
        response.qcontext['month_filter'] = month_filter

        amount_usd = orders.filtered(
            lambda rec: rec.state == 'sale'
            and rec.pricelist_id.currency_id.name == 'USD'
            ).mapped('amount_total')
        amount_total_usd = sum(amount_usd)
        response.qcontext['total_amount_usd'] = amount_total_usd

        amount_mxn = orders.filtered(
            lambda rec: rec.state == 'sale'
            and rec.currency_id.name == 'MXN'
            ).mapped('amount_total')
        amount_total_mxn = sum(amount_mxn)
        response.qcontext['total_amount_mxn'] = amount_total_mxn

        return response

    @http.route()
    def portal_my_quotes(self, *arg, **kw):
        response = super(MyAccountOrders, self).portal_my_quotes(*arg, **kw)
        quotations = response.qcontext.get('quotations')

        month_filter = kw.get('month')
        response.qcontext['month_filter'] = month_filter

        amount_usd = quotations.filtered(
            lambda rec: rec.state == 'sent'
            and rec.pricelist_id.currency_id.name == 'USD'
            ).mapped('amount_total')
        amount_total_usd = sum(amount_usd)
        response.qcontext['total_amount_usd'] = amount_total_usd

        amount_mxn = quotations.filtered(
            lambda rec: rec.state == 'sent'
            and rec.currency_id.name == 'MXN'
            ).mapped('amount_total')
        amount_total_mxn = sum(amount_mxn)
        response.qcontext['total_amount_mxn'] = amount_total_mxn

        return response


class MyAccount(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["name", "phone",
                                "email", "street",
                                "street2", "city", "country_id"]
    _items_per_page = 100

    @http.route(['/my/contact/edit'], type='http', auth='user', website=True)
    def contact_edit(self, redirect=None, **post):
        partner_obj = request.env['res.partner'].with_context(
            show_address=1).sudo()
        logued_partner = request.env.user.partner_id
        mode = (False, False)
        values = errors = {}
        # -1 When request comes from add user request
        partner_id = int(post.get('partner_id', -1))
        def_country_id = request.website.user_id.sudo().country_id
        # IF New contact
        if partner_id == -1:
            mode = ('new', 'shipping')
        # IF VALID PARTNER
        else:
            if partner_id <= 0:
                return request.redirect('/my/address')
            partner = partner_obj.browse(partner_id)
            if partner_id == logued_partner.id:
                mode = ('edit', 'billing')
            else:
                partner_shippings = logued_partner._get_partner_shippings()
                if partner_id in partner_shippings.mapped('id'):
                    mode = ('edit', 'shipping')
                else:
                    return Forbidden()
            if mode:
                values = partner
        # IF POSTED
        if 'submitted' in post:
            errors, error_msg = self._contact_details_validate(
                mode, post)
            if errors:
                errors['error_message'] = error_msg
                values = post
            else:
                contact_dict, errors, error_msg = self.values_postprocess(
                    logued_partner, mode, post, errors, error_msg)
                partner_id = self._contact_details_save(
                    mode, contact_dict, post)
                if not errors:
                    return request.redirect('/my/address')

        country = (
            'country_id' in values and values['country_id'] != '' and
            request.env['res.country'].browse(int(values['country_id'])))
        country = country and country.exists() or def_country_id
        render_values = {
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'active_page': '/my/address',
        }
        return request.render("typ.contact_edit", render_values)

    def _contact_details_validate(self, mode, data):
        # mode: tuple ('new|edit', 'billing|shipping')
        # data: values after preprocess
        error = dict()
        error_message = []
        # Required fields from mandatory field function
        required_fields = (
            mode[1] == 'shipping' and self._get_mandatory_shipping_fields() or
            self._get_mandatory_billing_fields())
        # Check if state required
        if data.get('country_id'):
            country = request.env['res.country'].browse(
                int(data.get('country_id')))
            if ('state_code' in country.get_address_fields() and
                    country.state_ids):
                required_fields += ['state_id']
        # error message for empty required fields
        for field_name in required_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'
        # email validation
        if (data.get('email') and
                not tools.single_email_re.match(data.get('email'))):
            error["email"] = 'error'
            error_message.append(
                _('Invalid Email! Please enter a valid email address.'))
        # vat validation
        partner = request.env["res.partner"]
        if data.get("vat") and hasattr(partner, "check_vat"):
            partner_dummy = partner.new({
                'vat': data['vat'],
                'country_id': (int(data['country_id'])
                               if data.get('country_id') else False),
            })
            try:
                partner_dummy.check_vat()
            except ValidationError:
                error["vat"] = 'error'
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))
        return error, error_message

    def _contact_details_save(self, mode, checkout, all_values):
        partner_obj = request.env['res.partner']
        if mode[0] == 'new':
            partner_id = partner_obj.sudo().create(checkout)
        elif mode[0] == 'edit':
            partner_id = int(all_values.get('partner_id', 0))
            if partner_id:
                partner = partner_obj.browse(partner_id)
                # double check
                shippings = partner._get_partner_shippings()
                if (partner_id not in shippings.mapped('id') and
                        partner_id != partner_id.id):
                    return Forbidden()
                partner_obj.browse(partner_id).sudo().write(checkout)
        return partner_id

    def _get_mandatory_shipping_fields(self):
        return WebsiteAccount()._get_mandatory_shipping_fields()

    def _get_mandatory_billing_fields(self):
        return WebsiteAccount()._get_mandatory_billing_fields()

    def values_postprocess(
            self, logued_partner, mode, values, errors, error_msg):
        new_values = {
            'customer': True,
            'team_id': (request.website.salesteam_id and
                        request.website.salesteam_id.id)
        }
        lang = (
            request.lang if request.lang in
            request.website.mapped('language_ids.code') else None)
        if lang:
            new_values['lang'] = lang
        if mode == ('edit', 'billing') and logued_partner.type == 'contact':
            new_values['type'] = 'other'
        if mode[1] == 'shipping':
            new_values['parent_id'] = logued_partner.commercial_partner_id.id
            new_values['type'] = 'delivery'
        new_values.update(values)
        new_values.pop('partner_id')
        new_values.pop('submitted')
        return new_values, errors, error_msg


class SendInvoiceAndXML(Controller):

    @http.route(
        ['/send_invoice_mail/<int:invoice_id>', ],
        type='http', auth='user', website=True)
    def send_invoice_and_xml(self, invoice_id=None, **data):
        invoice_obj = request.env['account.invoice']
        invoice = invoice_obj.browse(invoice_id)
        invoice.sudo().send_invoice_mail()
        values = {
            'company': request.website.company_id,
            'user': request.env.user,
            'invoice': invoice,
        }
        return request.render('typ.email_sent', values)


class WebsiteUserWishList(http.Controller):

    @http.route('/add_to_wishlist', type='json',
                auth='user', website=True)
    def add_wishlist_json(self, product_id):
        dic_wishlist = {}
        if product_id:
            dic_wishlist = {
                'product_template_id': int(product_id),
                'user_id': request.uid,
            }
        request.env['user.wishlist'].create(dic_wishlist)
        return True

    @http.route('/delete-order', type='http',
                auth='user', website=True)
    def delete_order(self):
        order = request.website.sale_get_order()
        if order:
            order.status = 'cancel'
            order.unlink()
        return request.redirect('/shop')

    @http.route(['/shop/duplicate_order/<model("sale.order"):order>'],
                type='http', auth="public", website=True)
    def duplicate_order(self, order, **kw):
        """Since the original `_cart_update` method is only useful for one
        product at the time, here we do a call per each line of the order and
        one single return to the cart.

        The `sudo()` call was necessary because old orders made via website
        include the delivery product which is not `website_published = True`
        this causes ACL errors, this implementation does not cause a hole
        of security because in the controller we are not sending `int` id of
        the order but a `sale.order` object which already has its own ACL.

        :param order: The order to duplicate.
        :type order: Recordset.

        :return: A redirection to the cart page.
        :rtype: Request redirect.
        """
        for order_l in order.order_line:
            if not order_l.sudo().product_id.sale_ok:
                continue
            request.website.sale_get_order(
                force_create=1)._cart_update(
                    product_id=int(order_l.product_id.id),
                    add_qty=float(order_l.product_uom_qty),
                    set_qty=float(order_l.product_uom_qty))
        return request.redirect("/shop/cart")
