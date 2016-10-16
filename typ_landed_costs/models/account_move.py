# -*- coding: utf-8 -*-

from openerp import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    guide_line_id = fields.Many2one(
        'stock.landed.cost.guide.line', help='Guide line associated to this'
        ' move')