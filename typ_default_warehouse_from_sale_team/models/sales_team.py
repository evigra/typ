# coding: utf-8

from openerp import fields, models


class CrmCaseSection(models.Model):

    _inherit = "crm.team"

    journal_guide_id = fields.Many2one(
        'account.journal', 'Journal landed cost guide',
        help='It indicates journal to be used when landed cost guide is'
        ' created')
    journal_landed_id = fields.Many2one(
        'account.journal', 'Journal landed cost',
        help='It indicates journal to be used when landed cost is created')
    sale_pricelist_id = fields.Many2one(
        'product.pricelist', 'Default sale pricelist',
        domain=[('type', '=', 'sale')], help='It indicates the sale pricelist'
        ' to be used when partner is created')
    purchase_pricelist_id = fields.Many2one(
        'product.pricelist', 'Default purchase pricelist',
        domain=[('type', '=', 'purchase')], help='It indicates the purchase '
        'pricelist to be used when partner is created')
