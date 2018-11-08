# -*- coding: utf-8 -*-

from openerp import models
from odoo.exceptions import AccessError


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def get_reconciliation_proposition(self, excluded_ids=None):
        res = super(AccountBankStatementLine,
                    self).get_reconciliation_proposition(excluded_ids)
        try:
            res.check_access_rule('read')
        except AccessError:
            return self.env['account.move.line']
        return res
