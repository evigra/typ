from odoo import fields, models


class ResConfiguration(models.TransientModel):

    _inherit = "res.config.settings"

    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.user.company_id
    )

    margin_allowed = fields.Float(
        related="company_id.margin_allowed",
        string="Margin Allowed on Sale Order",
        readonly=False,
        help="Percent (%) margin allowed to be modified on sales orders",
    )
