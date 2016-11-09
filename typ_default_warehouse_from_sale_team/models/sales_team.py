# coding: utf-8

from openerp import fields, models


class CrmCaseSection(models.Model):

    _inherit = "crm.case.section"

    journal_guide_id = fields.Many2one(
        'account.journal', 'Journal landed cost guide',
        help='It indicates journal to be used when landed cost guide is'
        ' created')
    journal_landed_id = fields.Many2one(
        'account.journal', 'Journal landed cost',
        help='It indicates journal to be used when landed cost is created')
