# -*- coding: utf-8 -*-

from openerp import models, api


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    # pylint: disable=W0622
    def _domain_move_lines_for_reconciliation(
            self, st_line, excluded_ids=None, str=False,
            additional_domain=None):

        if additional_domain is None:
            additional_domain = []

        additional_domain.append(
            ('account_id.type', 'in', ('payable', 'receivable')))
        return super(AccountBankStatementLine,
                     self)._domain_move_lines_for_reconciliation(
                         st_line, excluded_ids, str, additional_domain)
