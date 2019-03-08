# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd.
#    (<https://webkul.com/>)
#
###############################################################################
import logging
import psycopg2

from odoo import api, fields, models, tools
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    def _get_group_pos_allow_payment(self):
        return self.env.ref('typ_pos.allow_create_payment', False)

    wk_display_stock = fields.Boolean('Display stock in POS', default=True)

    wk_stock_type = fields.Selection(
        (
            ('available_qty', 'Available Quantity(On hand)'),
            ('forecasted_qty', 'Forecasted Quantity'),
            ('virtual_qty', 'Quantity on Hand - Outgoing Qty')
        ), string='Stock Type', default='available_qty')
    wk_continous_sale = fields.Boolean('Allow Order When Out-of-Stock')
    wk_deny_val = fields.Integer('Deny order when product stock is'
                                 ' lower than ')
    wk_error_msg = fields.Char(string='Custom message',
                               default="Product out of stock")
    wk_hide_out_of_stock = fields.Boolean(string="Hide Out of Stock products",
                                          default=True)
    crm_team_id = fields.Many2one(
        domain=[('team_type', 'in', ('pos', 'sales'))])

    group_pos_allow_payment_id = fields.Many2one(
        'res.groups', string='Point of Sale Allow Payment Group',
        default=_get_group_pos_allow_payment,
        help='This field is there to pass the id of the pos '
        'payment group to determinate if the current user '
        'should create the payment from UI POS')


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('use_session'):
            args = [
                ('state', '!=', 'closed'),
                ('crm_team_id', '=', self.env.user.sale_team_id.id)]
        return super(PosSession, self).search(
            args=args, offset=offset, limit=limit, order=order, count=count)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def refund(self):
        res = super(PosOrder, self.with_context(use_session=True)).refund()
        return res

    @api.multi
    def action_pos_order_paid(self):
        try:
            return super(PosOrder, self).action_pos_order_paid()
        except BaseException as e:
            if isinstance(e, psycopg2.OperationalError):
                raise
            _logger.error(
                'Could not fully process the POS Order: %s', tools.ustr(e))

    @api.multi
    def action_pos_order_invoice(self):
        res = super(PosOrder, self).action_pos_order_invoice()
        for order in self:
            order.invoice_id.get_payment_term()
        return res
