# coding: utf-8

from openerp import api, models


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.model
    def _get_product_supplier(self, procurement):
        """If the sale_order_line that generated the procurement has a
        Supplier for purchase (field purchase_partner_id), return it to create
        the purchase order with that partner.
        """
        if procurement.sale_line_id and \
                procurement.sale_line_id.purchase_partner_id:
            return procurement.sale_line_id.purchase_partner_id
        return super(ProcurementOrder, self)._get_product_supplier(
            procurement)
