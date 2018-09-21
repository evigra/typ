# coding: utf-8

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    type_payment_term = fields.Selection(
        [('credit', 'Credit'), ('cash', 'Cash'),
         ('postdated_check', 'Postdated check')], default='credit')

    @api.onchange('warehouse_id', 'partner_id')
    def _onchange_warehouse_id(self):
        """Obtain Salesman depending on configuration warehouse in partner
        related
        """
        res = super(SaleOrder, self)._onchange_warehouse_id()
        warehouse_config = self.partner_id.res_warehouse_ids.filtered(
            lambda wh_conf: wh_conf.warehouse_id == self.warehouse_id)
        if warehouse_config:
            self.user_id = warehouse_config.user_id.id
        return res

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        """Inherit to reassign origin field in procurement order"""
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id)
        res.update({'origin': order.name})
        return res

    @api.onchange('type_payment_term', 'partner_id')
    def get_payment_term(self):
        """Get payment term depends on type payment term.
        """
        self.env['account.invoice'].with_context(
            {'res_id': self}).get_payment_term()

    @api.onchange('order_line')
    def check_margin(self):
        """Verify margin minimum in sale order by change in field.
        """
        for line in self.order_line:
            warning = line.check_margin_qty()
            if warning:
                warning['title'] = _('Sale of product below margin')
                return {
                    'warning': warning,
                }

    @api.multi
    def action_cancel(self):
        picking_done = self.picking_ids.filtered(
            lambda pick: pick.state == 'done')
        if picking_done:
            raise ValidationError(_('This order can not be canceled because '
                                    'some of their pickings already have been '
                                    'transfered.'))
        return super(SaleOrder, self).action_cancel()


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.origin:
            new_origin = self.origin + ':' + self.name
            res.update({'origin': new_origin})
        return res
