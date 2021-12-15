from odoo import api, fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    is_immediate = fields.Boolean(compute="_compute_is_immediate", store=True)

    @api.depends("line_ids.days", "line_ids.option")
    def _compute_is_immediate(self):
        non_immediate_lines = self.env["account.payment.term.line"].read_group(
            domain=[
                ("payment_id", "in", self.ids),
                "|",
                ("option", "!=", "day_after_invoice_date"),
                ("days", "!=", 0),
            ],
            fields=["payment_id"],
            groupby=["payment_id"],
        )
        non_immediate_terms = {p["payment_id"][0] for p in non_immediate_lines}
        for term in self:
            term.is_immediate = term.id not in non_immediate_terms
