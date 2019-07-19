# coding: utf-8

from odoo import api, models


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    @api.multi
    def write(self, values):
        res = super(AccountJournal, self).write(values)
        if 'section_id' in values:
            self.clear_caches()
        return res
