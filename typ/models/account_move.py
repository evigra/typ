# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # Ticket 6482
    # Context: Typ instance has seriously performance issues, in a meeting with
    # Moy, Julio and Hugo, we deduct after a lot of analysis with pgbadger that
    # is needed the following:
    # - Overwrite payment_id field in order to add an index
    # - New Multicolumn Indexes on date and id fields

    payment_id = fields.Many2one('account.payment', index=True)

    @api.model
    def _auto_init(self):
        res = super(AccountMoveLine, self)._auto_init()
        index = 'account_move_line_date_id'
        self.env.cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index,))
        if not self.env.cr.fetchone():
            self.env.cr.execute('''
                CREATE INDEX account_move_line_date_id
                    ON account_move_line (date DESC, id DESC);''')
        return res
