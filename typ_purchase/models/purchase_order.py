# -*- coding: utf-8 -*-

from openerp import models, fields, api


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    shipment_date = fields.Datetime('order shipment date',
                                    help="this is used to indicate when "
                                    "products ships from supplier warehouse")
    buyer = fields.Char('Buyer', help="This is the buyer in charge of "
                        "the order's supplier")

    @api.onchange('partner_id')
    def _onchange_buyer(self):
        self.buyer = self.partner_id.buyer_id.name
