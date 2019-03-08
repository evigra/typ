# coding: utf-8
# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class AuthSignupHomeInherit(AuthSignupHome):

    @http.route('/theme/signup', type='http', auth='public', website=True)
    def theme_signup(self, *args, **kw):
        """This controller is added in order to return the context with errors
        info instead of returning a html DOM
        """
        res = self.web_auth_signup(*args, **kw)
        return json.dumps({
            'login_success': not res.qcontext.get("error"),
            'error': res.qcontext.get("error", False),
            'login': kw.get('login', False)
        })

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        res = super(AuthSignupHomeInherit, self).web_auth_reset_password(
            *args, **kw)
        qerror = res.qcontext.get('error', '')
        if qerror.endswith("'')"):
            res.qcontext.update(error=_(
                'There was a problem while resetting your password'))
        user = request.env['res.users'].search(
            [('login', '=', request.params.get("login"))])
        if (user and request.params.get("phone")):
            user.partner_id.sudo().write(
                {'phone': request.params.get("phone")})
        return res


class HomeInherit(Home):

    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super(HomeInherit, self).web_login(redirect=None, **kw)
        response.qcontext.update(on_login=True)
        return response

    @http.route('/theme/login', type='http', auth="none")
    def theme_login(self, redirect=None, **kw):
        """This controller is added in order to return the context with errors
        info instead of returning a html DOM
        """
        res = self.web_login(redirect, **kw)
        return json.dumps({
            'login_success': not res.qcontext.get("error"),
            'error': res.qcontext.get("error", False),
        })
