from odoo import fields, models


class StockLandedCost(models.Model):

    _inherit = "stock.landed.cost"

    def _get_account_journal_id(self):
        sale_team = self.env.user.sale_team_id
        return sale_team.journal_landed_id.id

    account_journal_id = fields.Many2one(
        "account.journal",
        "Account Journal",
        required=True,
        states={"done": [("readonly", True)]},
        default=_get_account_journal_id,
    )
