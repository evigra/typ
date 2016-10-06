# coding: utf-8

from openerp import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.onchange('warehouse_id', 'partner_id')
    def get_salesman_from_warehouse_config(self):
        """Obtain Salesman depending on configuration warehouse in partner
        related
        """
        res = self.onchange_warehouse_id(self.warehouse_id.id)
        for key in res.get('value').keys():
            if not hasattr(self, key):
                del res['value'][key]
        # Reasign values obtain in original onchange
        self.update(res['value'])
        warehouse_config = self.partner_id.res_warehouse_ids.filtered(
            lambda wh_conf: wh_conf.warehouse_id == self.warehouse_id)
        if warehouse_config:
            self.user_id = warehouse_config.user_id.id
