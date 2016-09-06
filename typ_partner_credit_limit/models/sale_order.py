# -*- coding: utf-8 -*-

from openerp import api, models, _


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.multi
    def onchange_partner_id(self, partner_id):
        """Show warning message if partner selected has no credit limit.
        """
        res = super(SaleOrder, self).onchange_partner_id(partner_id)
        partner = self.env['res.partner'].browse(partner_id)
        if not partner.allowed_sale:
            warning = {
                'title': _('Warning!'),
                'message': _('The partner selected has the credit closed.'),
            }
            res['warning'] = warning
        return res
