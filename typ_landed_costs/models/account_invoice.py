# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    guide_line_id = fields.Many2one(
        'stock.landed.cost.guide.line', help='Guide line associated to this'
        ' invoice')
