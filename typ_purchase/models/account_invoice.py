from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        purchase_model = self.env["purchase.order"]
        team_model = self.env["crm.team"]
        journal_model = self.env["account.journal"]
        res = super()._onchange_partner_id()
        if self.move_type in ("in_invoice", "in_refund") and self.state == "draft":
            currency_id = self.partner_id.property_purchase_currency_id
            if not currency_id:
                currency_id = self.env.user.company_id.currency_id
            sale_team_id = self.env.user.sale_team_id
            default_purchase_id = self._context.get("default_purchase_id")
            if default_purchase_id:
                purchase_id = purchase_model.browse(default_purchase_id)
                currency_id = purchase_id.currency_id
                warehouse_id = purchase_id.picking_type_id.warehouse_id
                sale_team_id = team_model.search([("default_warehouse", "=", warehouse_id.id)], limit=1)
            self.currency_id = currency_id
            self.journal_id = journal_model.search(
                [("section_id", "=", sale_team_id.id), ("type", "=", "purchase")], limit=1
            )
        return res
