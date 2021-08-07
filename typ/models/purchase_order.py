from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one("sale.order", "Sale Order", help="Reference to Sale Order")
    supply_commitment_date = fields.Date(
        states={"cancel": [("readonly", True)], "done": [("readonly", True)], "purchase": [("readonly", True)]},
        help="Date that the supplier undertakes to deliver.",
        copy=False,
    )
    shipment_date = fields.Date(
        "Order shipment date", help="This is used to indicate when " "products ships from supplier warehouse"
    )
    broker_id = fields.Many2one("res.partner", "Broker", help="Broker for imported products")
    report_lang = fields.Char(
        "Report Language",
        compute="_compute_report_lang",
        help="This field is automatically set from partner or broker language" " if exists",
    )
    buyer_id = fields.Many2one(
        related="partner_id.buyer_id",
        store=True,
        help="This is the buyer in charge of the order's vendor",
    )

    @api.model
    def _prepare_picking(self):
        res = super()._prepare_picking()
        if self.origin:
            new_origin = self.origin + ":" + self.name
            res.update({"origin": new_origin})
        return res

    @api.depends("partner_id", "broker_id")
    def _compute_report_lang(self):
        for record in self:
            record.report_lang = self.broker_id.lang or self.partner_id.lang

    @api.onchange("shipment_date")
    def _onchange_shipment_date(self):
        for line in self.order_line:
            line.update({"shipment_date": self.shipment_date})

    def button_cancel(self):
        """Allow cancel purchase order, related to special sale order with
        pickings in transit when their states aren`t done"""
        return super(PurchaseOrder, self.with_context(cancel_picking=True)).button_cancel()
