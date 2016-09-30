# coding: utf-8

from openerp import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    purchase_partner_id = fields.Many2one(
        'res.partner', string='Supplier for purchase',
        domain=[('supplier', '=', True)],
        help='In this field can be defined the supplier you want to make'
        ' the purchase that is generated by a special sale order.')
    special_sale = fields.Boolean(
        compute='_compute_is_special_sale',
        help='True if there is a buy type procurement rule within the chosen'
        ' route, otherwise false')

    @api.depends('route_id')
    def _compute_is_special_sale(self):
        for rec in self:
            pull_buy = rec.route_id.pull_ids.filtered(
                lambda dat: dat.action == 'buy')
            rec.special_sale = True if pull_buy else False
