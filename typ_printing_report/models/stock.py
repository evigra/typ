from odoo import models, fields


class StockMove(models.Model):

    _inherit = "stock.move"

    normalized_barcode = fields.Boolean(related="product_id.normalized_barcode")
    location_usage = fields.Selection(related="location_id.usage")
