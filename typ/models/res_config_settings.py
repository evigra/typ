from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    margin_allowed = fields.Float(
        related="company_id.margin_allowed",
        string="Margin Allowed on Sale Order",
        readonly=False,
        help="Percent (%) margin allowed to be modified on sales orders",
    )
    no_auto_scheduler = fields.Boolean(
        string="Don't auto run scheduler",
        default=True,
        # Param provided by Odoo. For more info, see:
        # https://github.com/odoo/odoo/pull/68203
        config_parameter="stock.no_auto_scheduler",
        help="Do not automatically check reordering rules when a product cannot be completely reserved, "
        "which avoids to have a replenishment document for the product without having run scheduler.",
    )
