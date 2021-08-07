from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    shipment_date = fields.Date(
        "Product shipment date",
        default=lambda self: self._default_shipment_date(),
        help="Indicate when product ships " "from supplier's warehouse",
    )

    @api.model
    def _default_shipment_date(self):
        date = self._context.get("shipment_date")
        return date or False

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        if res:
            suppliers = self.product_id.seller_ids.filtered(
                lambda r: r.name == self.order_id.partner_id and r.product_id == self.product_id
            )
            supplier = suppliers[:1]
            res[0].update(
                {"product_supplier_ref": supplier.product_code, "shipment_date": picking.picking_shipment_date}
            )
        return res
