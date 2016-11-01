# coding: utf-8

from openerp import api, fields, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    type_payment_term = fields.Selection(
        [('credit', 'Credit'), ('cash', 'Cash'),
         ('postdated_check', 'Postdated check')], default='credit',
        string='Type payment term')

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
        if self.partner_id:
            if self.type_payment_term in ('cash', 'postdated_check'):
                for payment_term in \
                        self.env['account.payment.term'].search([]):
                    if payment_term.payment_type == 'cash':
                        self.payment_term = payment_term.id
                        break
            else:
                self.payment_term = self.partner_id.property_payment_term.id
            if self.type_payment_term == 'credit' and \
                    (not self.payment_term or
                        self.payment_term.payment_type == 'cash'):
                self.type_payment_term = 'cash'
            elif self.type_payment_term in ('cash', 'postdated_check') and \
                    self.payment_term.payment_type == 'credit':
                self.type_payment_term = 'credit'
