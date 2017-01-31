# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    exchange_landed_ids = fields.Many2many(
        'stock.landed.cost',
        'landed_invoice_rel',
        'invoice_id', 'landed_id',
        copy=False,
        string='Exchange Differential Landed',
        help='Landed created to adjust '
        'the cost of the product by '
        'exchange differential')

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        res['guide_line_id'] = line.get('guide_line_id', False)
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    guide_line_id = fields.Many2one(
        'stock.landed.cost.guide.line', help='Guide line associated to this'
        ' invoice')

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        res['guide_line_id'] = line.guide_line_id.id
        return res
