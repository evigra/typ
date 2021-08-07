from odoo import fields, models


class CrmTeam(models.Model):
    _inherit = "crm.team"

    sale_phone = fields.Char(string="Phone", help="Phone for contact sales team")
    fiscal_position_id = fields.Many2one(
        "account.fiscal.position",
        string="Fiscal position",
        help="It indicates the fiscal position to be used when sale order is created",
    )
    journal_guide_id = fields.Many2one(
        "account.journal",
        string="Journal landed cost guide",
        help="It indicates journal to be used when landed cost guide is created",
    )
    journal_landed_id = fields.Many2one(
        "account.journal",
        string="Journal landed cost",
        help="It indicates journal to be used when landed cost is created",
    )
    sale_pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Default Sales Pricelist",
        help="It indicates the sales pricelist to be used when partner is created",
    )
