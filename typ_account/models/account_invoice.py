# -*- coding: utf-8 -*-

from openerp import exceptions, models, api, fields, _


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    user_id = fields.Many2one('res.users', string='Salesperson',
                              track_visibility='onchange', readonly=False,
                              default=lambda self: self.env.user)
    validation_date = fields.Date('Invoice validation date',
                                  help="This date indicate "
                                  "when the invoice was validated")
    date_paid = fields.Date('Payment date', index=True, copy=False,
                            help="This date indicate when the invoice "
                            "was paid")

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
            if invoice.payment_term_id.payment_type != 'credit':
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
                        '\nCredit'
                        ' Limit : %s') % (credit_limit)
                raise exceptions.Warning(msg)

    @api.onchange('partner_id', 'journal_id', 'company_id')
    def _onchange_partner_id(self):
        """Show warning message if partner selected has no credit limit.
        """
        res = super(AccountInvoice, self)._onchange_partner_id()
        ctx = {'new_amount': self.amount_total,
               'new_currency': self.currency_id.id,
               'journal_id': self.journal_id.id}
        res_partner = self.env['res.partner'].with_context(ctx)
        allowed_sale = res_partner.browse(self.partner_id.id).allowed_sale
        if not self.partner_id or allowed_sale:
            return res
        credit_overloaded = res_partner.browse(
            self.partner_id.id).credit_overloaded
        overdue_credit = res_partner.with_context(
            {'journal_id': self.journal_id.id}).browse(
                self.partner_id.id).overdue_credit
        msg = _('The partner ')
        if credit_overloaded:
            msg = msg + _('%s has credit overloaded')
            if overdue_credit:
                msg = msg + _(' and has overdue invoices')
        elif overdue_credit:
            msg = msg + _('%s has overdue invoices')
        msg = msg + _('. Please request payment or sell cash!')
        warning = {
            'title': _('Warning!'),
            'message': ((msg) % self.partner_id.name),
        }
        res['warning'] = warning
        return res

    @api.model
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        validation_date = fields.Date.context_today(self)
        self.write({'validation_date': validation_date})
        return res

    @api.multi
    def confirm_paid(self):
        res = super(AccountInvoice, self).confirm_paid()
        date_paid = fields.Date.context_today(self)
        self.write({'date_paid': date_paid})
        return res
