# -*- coding: utf-8 -*-

from openerp import models, api, _
from openerp import exceptions


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def need_verify_limit_credit(self):
        """Verify only client invoices.
        """
        self.ensure_one()
        if self.type != 'out_invoice':
            return False
        return True

    @api.multi
    def check_limit_credit(self):
        for invoice in self:
            if not invoice.need_verify_limit_credit():
                return True
            if invoice.payment_term.payment_type != 'credit':
                return True
            allowed_sale = self.env['res.partner'].with_context(
                {'new_amount': invoice.amount_total,
                 'new_currency': invoice.currency_id.id,
                 'journal_id': invoice.journal_id.id}).browse(
                     invoice.partner_id.id).allowed_sale
            if allowed_sale:
                return True
            else:
                default_sale_team = invoice.journal_id.section_id
                warehouse_id = default_sale_team.default_warehouse.id
                wh_config = invoice.partner_id.res_warehouse_ids.filtered(
                    lambda wh_conf: wh_conf.warehouse_id.id == warehouse_id)
                credit_limit = wh_config.credit_limit if wh_config else \
                    invoice.partner_id.credit_limit
                msg = _('Can not validate the Invoice because Partner '
                        'has late payments or has exceeded the credit limit.'
                        '\nPlease cover the late payment or check credit limit'
                        '\nCreadit'
                        ' Limit : %s') % (credit_limit)
                raise exceptions.Warning(_('Warning!'), msg)

    @api.onchange('partner_id', 'journal_id')
    def get_partner_allowed_sale(self):
        """Show warning message if partner selected has no credit limit.
        """
        res = self.onchange_partner_id(
            self.type, self.partner_id.id, self.date_invoice,
            self.payment_term.id, self.partner_bank_id.id, self.company_id.id)
        for key in res.get('value').keys():
            if not hasattr(self, key):
                del res['value'][key]
        # Reasign values obtain in original onchange
        self.update(res['value'])
        allowed_sale = self.env['res.partner'].with_context(
            {'journal_id': self.journal_id.id}).browse(
                self.partner_id.id).allowed_sale
        if self.partner_id and not allowed_sale:
            warning = {
                'title': _('Warning!'),
                'message': _('The partner selected has the credit closed.'),
            }
            res['warning'] = warning
        return res
