from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_cedis = fields.Boolean(
        string="Receive to CEDIS?",
        compute="_compute_is_cedis",
        store=True,
        help="Indicates wheter this operation tipe is used to receive products to a distribution center.",
    )

    @api.depends("warehouse_id.is_cedis", "code")
    def _compute_is_cedis(self):
        for record in self:
            record.is_cedis = record.warehouse_id.is_cedis and record.code == "incoming"
