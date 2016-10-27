# -*- coding: utf-8 -*-

from openerp import models, fields


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    shipment_date = fields.Datetime('Product shipment date')
