from odoo import fields, models


class CrmTeam(models.Model):

    _inherit = "crm.team"

    sale_phone = fields.Char(string="Phone", help="Phone for contact sale team")
    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal position",
        help="It indicates the fiscal position" " to be used when sale order is created",
    )
