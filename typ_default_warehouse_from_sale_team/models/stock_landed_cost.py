# coding: utf-8

from openerp import api, fields, models


class StockLandedCost(models.Model):

    _inherit = 'stock.landed.cost'

    @api.multi
    def _get_account_journal_id(self):
        sale_team = self.env.user.default_section_id
        return sale_team.journal_landed_id.id

    account_journal_id = fields.Many2one(
        'account.journal', 'Account Journal', required=True,
        states={'done': [('readonly', True)]}, default=_get_account_journal_id,
    )
