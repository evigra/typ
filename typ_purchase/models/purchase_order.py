
from odoo import models, fields, api


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    shipment_date = fields.Date('Order shipment date',
                                help="This is used to indicate when "
                                "products ships from supplier warehouse")
    broker_id = fields.Many2one(
        'res.partner', "Broker", help="Broker for imported products")
    buyer = fields.Many2one(
        related='partner_id.buyer_id',
        relation='res.users',
        readonly=True,
        store=True,
        help="This is the buyer in charge of the order's supplier")
    report_lang = fields.Char(
        'Report Language', compute="_compute_report_lang",
        help="This field is automatically set from partner or broker language"
        " if exists")

    @api.depends('partner_id', 'broker_id')
    def _compute_report_lang(self):
        for record in self:
            record.report_lang = self.broker_id.lang or self.partner_id.lang

    @api.multi
    @api.onchange('shipment_date')
    def _onchange_shipment_date(self):
        for line in self.order_line:
            line.update({'shipment_date': self.shipment_date})

    @api.multi
    def button_cancel(self):
        """Allow cancel purchase order, related to special sale order with
        pickings in transit when their states aren`t done"""
        return super(PurchaseOrder, self.with_context(
            cancel_picking=True)).button_cancel()
