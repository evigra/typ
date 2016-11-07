# -*- coding: utf-8 -*-

from openerp import models, fields


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    shipment_date = fields.Datetime('order shipment date',
                                    help="this is used to indicate when "
                                    "products ships from supplier warehouse")
    buyer = fields.Many2one(
        related='partner_id.buyer_id',
        relation='res.users',
        readonly=True,
        store=True,
        help="This is the buyer in charge of the order's supplier")
