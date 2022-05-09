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
    purchase_partner_id = fields.Many2one(
        "res.partner",
        string="Vendor for purchase",
        readonly=True,
        help="Custom vendor to be used when creating a purchase order.",
    )

    def _prepare_procurement_values(self):
        """Consider purchase vendor

        If we're comming from a special sale order:
        - If in last step (buy rule), use the specified vendor when creating the purchase order
        - If in an intermediate rule, propagate vendor to next moves so it's available when running buy rule
        """
        values = super()._prepare_procurement_values()
        if self.purchase_partner_id:
            values.update(
                {
                    "purchase_partner_id": self.purchase_partner_id.id,
                    "supplierinfo_name": self.purchase_partner_id,
                }
            )
        return values
