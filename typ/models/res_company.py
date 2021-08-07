from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    margin_allowed = fields.Float(
        default="10.0",
        string="Margin Allowed on Sale Order",
        help="Percent (%) margin allowed to be modified on sales orders",
    )
    report_id = fields.Many2one("ir.actions.report", "Label report", domain="[('model','=','product.product')]")
    email_purchase = fields.Char()
