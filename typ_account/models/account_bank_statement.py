
from odoo import models, api


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def get_reconciliation_proposition(self, excluded_ids=None):
        # Ticket 6482
        # Context: Typ instance has seriously performance issues, in a meeting
        # with Moy, Julio, deduct after a lot of analysis with
        # pgbadger that is needed the following:

        return self.env['account.move.line']

    @api.multi
    def auto_reconcile(self):
        return False


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    @api.multi
    def reconciliation_widget_preprocess(self):
        """ Inherit method to avoid assigning a partner.
        """
        st_lines_old = self.mapped('line_ids').filtered(
            lambda l: not l.partner_id)
        res = super().reconciliation_widget_preprocess()
        st_lines = self.env['account.bank.statement.line'].browse(
            res['st_lines_ids'])
        (st_lines & st_lines_old).write({
            'partner_id': False
        })
        return res
