# -*- coding: utf-8 -*-

from openerp import api, models, _
from openerp import exceptions


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.onchange('partner_id', 'warehouse_id')
    def get_partner_allowed_sale(self):
        """Show warning message if partner selected has no credit limit.
        """
        res_partner = self.env['res.partner']
        res = self.onchange_partner_id(self.partner_id.id)
        for key in res.get('value').keys():
            if not hasattr(self, key):
                del res['value'][key]
        # Reasign values obtain in original onchange
        self.update(res['value'])
        allowed_sale = res_partner.with_context(
            {'warehouse_id': self.warehouse_id.id}).browse(
                self.partner_id.id).allowed_sale
        if self.partner_id and not allowed_sale:
            credit_overloaded = res_partner.with_context(
                {'warehouse_id': self.warehouse_id.id}).browse(
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
            res['warning'] = warning
        return res

    @api.multi
    def check_limit(self):
        for so in self:
            if so.payment_term.payment_type != 'credit':
                return True
            allowed_sale = self.env['res.partner'].with_context(
                {'new_amount': so.amount_total,
                 'new_currency': so.company_id.currency_id.id,
                 'warehouse_id': self.warehouse_id.id}).browse(
                     so.partner_id.id).allowed_sale
            if allowed_sale:
                return True
            else:
                wh_config = so.partner_id.res_warehouse_ids.filtered(
                    lambda wh_conf:
                    wh_conf.warehouse_id.id == self.warehouse_id.id)
                credit_limit = wh_config.credit_limit if wh_config else \
                    so.partner_id.credit_limit
                msg = _('Can not confirm the Sale Order because Partner '
                        'has late payments or has exceeded the credit limit.'
                        '\nPlease cover the late payment or check credit limit'
                        '\nCredit Limit : %s') % (credit_limit)
                raise exceptions.Warning(_('Warning!'), msg)
