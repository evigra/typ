# coding: utf-8

from openerp import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def get_domain_pricelist(self):
        """Set domain depending on list of sale ricelist available by
        partner_id.
        """
        res = self.onchange_partner_id(self.partner_id.id)
        for key in res.get('value').keys():
            if not hasattr(self, key):
                del res['value'][key]
        # Reasign values obtain in original onchange
        self.update(res['value'])
        if self.partner_id.pricelist_ids:
            domain = {'pricelist_id': [('id', 'in', (
                self.partner_id.pricelist_ids.filtered(
                    lambda pricelist: pricelist.type == 'sale')).ids)]}
            return {'domain': domain}
