# -*- coding: utf-8 -*-

from odoo import models, api
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


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def reconciliation_widget_preprocess(self):
        """ Inherit method to avoid assigning a partner.
        """
        st_lines_old = [l.id for l in self.line_ids.filtered(
            lambda l: not l.partner_id)]
        res = super().reconciliation_widget_preprocess()
        st_lines = self.env['account.bank.statement.line'].browse(
            res['st_lines_ids'])
        (st_lines & st_lines_old).write({
            'partner_id': False
        })
        return res
