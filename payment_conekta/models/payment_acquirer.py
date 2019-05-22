# -*- coding: utf-8 -*-
# © 2017 Vauxoo, S.A. de C.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import conekta
except (ImportError, IOError) as err:
    _logger.debug(err)


def get_error_message(exception):
    message = exception.error_json.get('message')
    if not message:
        details = exception.error_json.get('details')
        message = details and details[0].get('message')
    return message


class AcquirerConekta(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('conekta', 'Conekta')])
    conekta_public_key = fields.Char(required_if_provider='conekta')
    conekta_private_key = fields.Char(required_if_provider='conekta')

    @api.multi
    def conekta_get_form_action_url(self):
        self.ensure_one()
        return '/shop/payment/validate'

    @api.model
    def conekta_s2s_form_process(self, data):
        payment_token = self.env['payment.token'].sudo().create({
            'name': data['cc_number'],
            'acquirer_ref': data['token_id'],
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id']),
            'verified': True
        })
        return payment_token

    @api.multi
    def conekta_s2s_form_validate(self, data):
        self.ensure_one()
        # mandatory fields
        for field_name in ["cc_number"]:
            if not data.get(field_name):
                return False
        return True

    def _get_feature_support(self):
        support = super()._get_feature_support()
        tokenized = support.get('tokenize')
        tokenized.append('conekta')
        return support


class PaymentTransactionStripe(models.Model):
    _inherit = 'payment.transaction'

    @api.multi
    def conekta_s2s_do_transaction(self, **data):
        self.ensure_one()
        result = self._create_conekta_charge()
        tree = self._conekta_s2s_validate_tree(result)
        return tree

    @api.multi
    def _create_conekta_charge(self, **data):
        payment_acquirer = self.env['payment.acquirer']
        conekta_acq = payment_acquirer.sudo().search(
            [('provider', '=', 'conekta')])
        conekta.api_key = conekta_acq.conekta_private_key
        params = self._create_conekta_params('conekta')
        try:
            conekta_res = conekta.Order.create(params)
        except conekta.ConektaError as error:
            return error
        return conekta_res

    def _conekta_build_payload(self, params):
        line_items = [{
            'name': line.product_id.name,
            'description': (line.product_id.description_sale if
                            line.product_id.description_sale else
                            line.product_id.name),
            'unit_price': int(line.price_subtotal * 100),
            'quantity': 1,
            'sku': line.product_id.default_code,
            'category': line.product_id.categ_id.name,
        } for line in params.get('lines')]
        partner = params.get('partner')
        partner_invoice = params.get('partner_invoice')
        phone_number = ''.join([n for n in (partner.phone or
                                partner.parent_id.phone or
                                partner.company_id.phone)
                                if n.isdigit()])
        billing_address = {
            'street1': partner_invoice.street,
            'street2': partner_invoice.street2,
            'city': partner_invoice.city,
            'state': partner_invoice.state_id.code,
            'zip': partner_invoice.zip,
            'country': partner_invoice.country_id.name,
            'tax_id': partner_invoice.vat,
            'company_name': (
                partner_invoice.parent_name or
                partner_invoice.name),
            'phone': phone_number,
            'email': self.env.user.partner_id.email,
        }
        shipping_lines = [{
            'amount': params.get('delivery_amount'),
            'carrier': params.get('delivery_carrier'),
            'currency': params.get('currency_invoice'),
        }]
        details = {
            'billing_address': billing_address,
            'name': partner.name,
            'phone': phone_number,
            'email':  self.env.user.partner_id.email,
            'customer': {
                'logged_in': False,
            }
        }
        charges = [{
            'payment_method': {
                'type': "card",
                'token_id': params.get('card'),
            }
        }]
        delivery_address = params.get('delivery_address')
        shipping_contact = {
            'address': {
                'street1': delivery_address.street,
                'street_number': delivery_address.street_number,
                'postal_code': delivery_address.zip,
                'country': delivery_address.country_id.name,
            },
        }
        taxes_lines = [{
            'description': "taxes",
            'amount': params.get('taxes'),
            'currency': params.get('currency_invoice'),
        }]
        return {
            'line_items': line_items,
            'shipping_lines': shipping_lines,
            'currency': params.get('currency_invoice'),
            'customer_info': details,
            'shipping_contact': shipping_contact,
            'description': params.get('name'),
            'tax_lines': taxes_lines,
            'amount': params.get('amount_invoice'),
            'metadata': {
                'reference_id': params.get('reference_id'),
            },
            'charges': charges,
        }

    def _create_conekta_params(self, acquirer):
        values = self.get_reference()
        if values['order']:
            order = values['order']
            params = {
                'name': _('%s Order %s') % (
                    order.company_id.name, order.name),
                'lines': order.order_line,
                'partner_invoice': order.partner_invoice_id,
                'amount_invoice': int(order.amount_total * 100),
                'currency_invoice': order.currency_id.name,
                'partner': order.partner_id,
                'reference_id': order.name,
                'taxes': int(order.amount_tax * 100),
                'delivery_amount': 0,
                'delivery_carrier': "No delivery line",
                'delivery_address': order.partner_shipping_id,
                'card': self.payment_token_id.acquirer_ref
            }
        else:
            invoice = values['invoice']
            params = {
                'name': _('%s Invoice %s') % (
                    invoice.company_id.name, invoice.number),
                'lines': invoice.invoice_line_ids,
                'partner_invoice': invoice.partner_id,
                'amount_invoice': int(invoice.amount_total * 100),
                'currency_invoice': invoice.currency_id.name,
                'partner': invoice.partner_id,
                'reference_id': invoice.number,
                'taxes': int(invoice.amount_tax * 100),
                'delivery_amount': 0,
                'delivery_carrier': "No delivery line",
                'delivery_address': invoice.partner_shipping_id,
                'card': self.payment_token_id.acquirer_ref
            }
        return self._conekta_build_payload(params)

    def search_reference(self, payment_reference):
        invoice = self.env['account.invoice'].search(
            [('number', '=', payment_reference)])
        order = self.env['sale.order'].search(
            [('name', '=', payment_reference)])
        values = {
            'order': order,
            'invoice': invoice,
        }
        return values

    def get_reference(self):
        reference_name = self.reference
        payment_reference = 'x'.join(reference_name.split('x')[:-1])
        if payment_reference:
            values = self.search_reference(payment_reference)
        else:
            values = self.search_reference(reference_name)
        return values

    @api.multi
    def _conekta_s2s_validate_tree(self, tree):
        self.ensure_one()
        values = self.get_reference()
        if isinstance(tree, conekta.ConektaError):
            message = get_error_message(tree)
            _logger.error(_("Error in Conekta transaction: %s"), message)
            self.write({
                'state': 'error',
                'state_message': message,
            })
            self.payment_token_id.unlink()
            return False
        if tree.payment_status == 'paid':
            invoice = values['invoice']
            self.write({
                'account_invoice_id': invoice.id,
                'state': 'done',
                'acquirer_reference': tree.id,
            })
            if invoice:
                self._confirm_invoice()
            self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.active = False
            return True
        if self.state not in ('draft', 'pending', 'refunding'):
            _logger.info(
                'Conekta: trying to validate an already validated tx (ref %s)',
                self.reference)
        return True

    @api.model
    def _conekta_form_get_tx_from_data(self, data):
        reference = data['reference_id']
        payment_tx = self.search([('reference', '=', reference)])
        if not payment_tx or len(payment_tx) > 1:
            error_msg = _(
                'Conekta: received data for reference %s') % reference
            if not payment_tx:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return payment_tx

    @api.model
    def _conekta_form_validate(self, data):
        date = datetime.datetime.fromtimestamp(
            int(data['paid_at'])).strftime('%Y-%m-%d %H:%M:%S')
        data = {
            'acquirer_reference': data['id'],
            'date': date,
            'state': 'done',
        }
        self.write(data)
