# -*- coding: utf-8 -*-

from openerp import api, models, _
from openerp import exceptions


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.onchange('partner_id', 'warehouse_id')
    def onchange_partner_id(self):
        """Show warning message if partner selected has no credit limit.
        """
        res_partner = self.env['res.partner']
        res = super(SaleOrder, self).onchange_partner_id()
        ctx = {'new_amount': self.amount_total,
               'new_currency': self.currency_id.id,
               'warehouse_id': self.warehouse_id.id}
        allowed_sale = res_partner.with_context(ctx).browse(
            self.partner_id.id).allowed_sale
        partner_payment_term_id = self.partner_id.property_payment_term_id
        is_cash = (self.type_payment_term in ('cash', 'postdated_check') or
                   not partner_payment_term_id
                   or partner_payment_term_id.payment_type == 'cash')
        if (not partner_payment_term_id and is_cash and
                not self.payment_term_id):
            self.payment_term_id = self.env.ref(
                'account.account_payment_term_immediate')
        if all([self.partner_id, not is_cash, not allowed_sale]):
            credit_overloaded = res_partner.with_context(ctx).browse(
                self.partner_id.id).credit_overloaded
            overdue_credit = res_partner.with_context(
                {'warehouse_id': self.warehouse_id.id}).browse(
                    self.partner_id.id).overdue_credit
            msg = _('The partner ')
            if overdue_credit:
                msg = msg + _('%s has overdue invoices')
                if credit_overloaded:
                    msg = msg + _(' and credit overloaded')
            elif credit_overloaded:
                msg = msg + _('%s has credit overloaded')
            msg = msg + _('. Please request payment or sell cash!')
            warning = {
                'title': _('Warning!'),
                'message': ((msg) % self.partner_id.name),
            }
            return {'warning': warning}
        return res

    @api.multi
    def check_limit(self):
        for so in self.filtered(
                lambda dat: dat.payment_term_id.payment_type == 'credit'):
            allowed_sale = self.env['res.partner'].with_context(
                {'new_amount': so.amount_total,
                 'new_currency': so.currency_id.id,
                 'warehouse_id': self.warehouse_id.id}).browse(
                     so.partner_id.id).allowed_sale
            if allowed_sale:
                return True
            wh_config = so.partner_id.res_warehouse_ids.filtered(
                lambda wh_conf:
                wh_conf.warehouse_id.id == self.warehouse_id.id)
            credit_limit = wh_config.credit_limit if wh_config else \
                so.partner_id.credit_limit
            msg = _('Can not confirm the Sale Order because Partner '
                    'has late payments or has exceeded the credit limit.'
                    '\nPlease cover the late payment or check credit limit'
                    '\nCredit Limit : %s') % (credit_limit)
            raise exceptions.Warning(msg)
