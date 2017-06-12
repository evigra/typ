# coding: utf-8

from openerp import api, models, fields


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    sale_line_id = fields.Many2one('sale.order.line', select=True)

    @api.model
    def _get_sale_line_id(self):
        """Get sale_line_id from a procurement_order register.
        """
        move_sale_line_id = self.sale_line_id
        parent = self.move_dest_id
        while not move_sale_line_id and parent:
            move_sale_line_id = parent.procurement_id.sale_line_id
            parent = parent.procurement_id.move_dest_id
        return move_sale_line_id

    @api.model
    def _get_product_supplier(self, procurement):
        """If the sale_order_line that generated the procurement has a
        Supplier for purchase (field purchase_partner_id), return it to create
        the purchase order with that partner.
        """
        return procurement._get_sale_line_id().purchase_partner_id or \
            super(ProcurementOrder, self)._get_product_supplier(procurement)
