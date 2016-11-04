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
        sale_line_id = procurement.sale_line_id or \
            procurement.move_dest_id.procurement_id.sale_line_id
        return sale_line_id.purchase_partner_id or \
            super(ProcurementOrder, self)._get_product_supplier(procurement)
