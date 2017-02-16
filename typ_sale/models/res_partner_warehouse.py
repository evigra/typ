# coding: utf-8

from openerp import fields, models


class ResPartnerWarehouse(models.Model):

    _name = 'res.partner.warehouse'

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   help='Set the warehouse')
    user_id = fields.Many2one('res.users', string='Salesperson')
    credit_limit = fields.Float()
    allow_overdue_invoice = fields.Boolean('Allow overdue invoices')
    partner_id = fields.Many2one('res.partner', string='Partner')
