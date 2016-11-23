# -*- coding: utf-8 -*-

from openerp import models, fields


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _default_shipment_date(self):
        date = self._context.get('shipment_date', False)
        return date
    shipment_date = fields.Date('Product shipment date',
                                default=_default_shipment_date,
                                help="Indicate when product ships "
                                "from supplier's warehouse")
