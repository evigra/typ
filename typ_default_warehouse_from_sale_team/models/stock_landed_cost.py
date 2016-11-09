# coding: utf-8

from openerp import api, fields, models


class StockLandedCost(models.Model):

    _inherit = 'stock.landed.cost'

    @api.multi
    def _get_account_journal_id(self):
        sale_team = self.env.user.default_section_id
        return sale_team.journal_landed_id.id

    def _get_domain_account_journal_id(self):
        """Search the Sale Team that is by default in user connected and set
        Journals associated to this Sale Team in domain"""
        sale_team = self.env.user.default_section_id
        domain = []
        if sale_team:
            journals = sale_team.journal_team_ids.ids
            domain = [('id', 'in', journals)] if journals else []
        return domain

    account_journal_id = fields.Many2one(
        'account.journal', 'Account Journal', required=True,
        states={'done': [('readonly', True)]}, default=_get_account_journal_id,
        domain=_get_domain_account_journal_id)
