from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    map_location = fields.Text(
        string='Google Maps Location',
        help='Embeded url from google maps')

    @api.model
    def _get_partner_shippings(self):
        self.ensure_one()
        shippings = self.search([
            ("id", "child_of", self.commercial_partner_id.ids),
            '|', ("type", "=", "delivery"),
            ("id", "=", self.commercial_partner_id.id)
        ], order='id desc')
        return shippings

    @api.model
    def _get_my_quotations(self, limit=6):
        self.ensure_one()
        sale_order = self.env['sale.order']
        domain = [
            ('message_partner_ids', 'child_of',
             [self.commercial_partner_id.id]),
            ('state', 'in', ['sent', 'cancel'])
        ]
        return sale_order.search(domain, limit=limit)

    @api.model
    def _get_my_orders(self, limit=None):
        self.ensure_one()
        sale_order = self.env['sale.order']
        domain = [
            ('message_partner_ids', 'child_of',
             [self.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ]
        return sale_order.search(domain, limit=limit)

    @api.model
    def _get_my_invoices(self, limit=None):
        self.ensure_one()
        acc_invoice = self.env['account.invoice']
        domain = [
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('message_partner_ids', 'child_of',
             [self.commercial_partner_id.id]),
            ('state', 'in', ['open', 'paid', 'cancel'])
        ]
        return acc_invoice.search(domain, limit=limit)
