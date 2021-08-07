from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    warranty_location = fields.Boolean(
        "Is a Warranty Location?",
        help="Check this box to allow the use of this location for warranties in process.",
    )
