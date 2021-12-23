from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    sale_line_id = fields.Many2one(index=True)
    shipment_date = fields.Date(
        "Product shipment date",
        default=fields.Date.context_today,
        index=True,
        states={"done": [("readonly", True)]},
        help="Scheduled date for the shipment of this move",
    )
    product_supplier_ref = fields.Char(string="Supplier Code")
    product_shipment_date = fields.Date(
        related="picking_id.picking_shipment_date", help="Product picking shipment date"
    )
    normalized_barcode = fields.Boolean(related="product_id.normalized_barcode")
    location_usage = fields.Selection(related="location_id.usage")
