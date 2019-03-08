# coding: utf-8

from __future__ import division
from openerp import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    purchase_partner_id = fields.Many2one(
        'res.partner', string='Supplier for purchase',
        domain=lambda self: [
            ('id', 'in',
             self.product_id.seller_ids.search([]).mapped('name').ids)],
        help='In this field can be defined the supplier you want to make'
        ' the purchase that is generated by a special sale order.')
    special_sale = fields.Boolean(
        compute='_compute_is_special_sale',
        help='True if there is a buy type procurement rule within the chosen'
        ' route, otherwise false')

    @api.multi
    def button_cancel(self):
        res = super(SaleOrderLine, self).button_cancel()
        for sale_line in self.filtered('order_id.pos'):
            move_ids = self.env['stock.move'].search([
                ('sale_order_line_id', '=', sale_line.id)])
            move_ids.action_cancel()
        return res

    @api.depends('route_id')
    def _compute_is_special_sale(self):
        for rec in self:
            pull_buy = rec.route_id.pull_ids.filtered(
                lambda dat: dat.action == 'buy')
            rec.special_sale = bool(pull_buy)

    @api.constrains('state')
    def check_margin(self):
        """Verify margin minimum in sale order line.
        """
        for sale_line in self:
            warning = sale_line.check_margin_qty(sale_line.price_subtotal)
            if warning:
                raise ValidationError(warning.get('message'))

    @api.onchange('price_unit')
    def onchange_check_margin(self):
        """Verify margin minimum in sale order line by change in field.
        """
        return {'warning': self.check_margin_qty()}

    def check_margin_qty(self, price_subtotal=False):
        """Verify quantity of margin minimum in sale order line for onchange.
        """
        res = {
            'message': _('You can not be sold the product %s below permitted '
                         'margin\nContact Manager') % (self.product_id.name)}
        if self.env.user.has_group(
                'typ_sale.res_group_can_sell_below_minimum_margin'):
            return
        if not price_subtotal:
            price_subtotal = self.price_subtotal

        if price_subtotal == 0 and not self.product_id:
            return

        if price_subtotal <= 0 and self.product_id:
            return res

        cur = self.order_id.pricelist_id.currency_id
        margin = self.env.user.company_id.margin_allowed
        if self.product_id and self.product_id.standard_price:
            tmp_standard_price = self.env.user.company_id.currency_id.compute(
                self.product_id.standard_price, cur)
            tmp_margin = price_subtotal - (tmp_standard_price *
                                           self.product_uom_qty)
        else:
            tmp_margin = price_subtotal - (self.purchase_price *
                                           self.product_uom_qty)

        purchase_sale = cur.round(tmp_margin)

        margin_sale = (purchase_sale / price_subtotal) * 100
        if margin_sale < margin:
            return res


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _make_po_select_supplier(self, values, suppliers):
        move = values.get('move_dest_ids')
        while move and move.move_dest_ids:
            move = move.move_dest_ids
        if move and move.sale_line_id.purchase_partner_id:
            partner_id = move.sale_line_id.purchase_partner_id
            suppliers = move.product_id.seller_ids.search(
                [('name', 'in', partner_id.ids)])
        res = super(ProcurementRule, self)._make_po_select_supplier(
            values, suppliers)
        return res
