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
                        '\nCredit'
                        ' Limit : %s') % (credit_limit)
                raise exceptions.Warning(_('Warning!'), msg)

    @api.onchange('partner_id', 'journal_id')
    def get_partner_allowed_sale(self):
        """Show warning message if partner selected has no credit limit.
        """
        res_partner = self.env['res.partner']
        res = self.onchange_partner_id(
            self.type, self.partner_id.id, self.date_invoice,
            self.payment_term.id, self.partner_bank_id.id, self.company_id.id)
        for key in res.get('value').keys():
            if not hasattr(self, key):
                del res['value'][key]
        # Reasign values obtain in original onchange
        self.update(res['value'])
        ctx = {'new_amount': self.amount_total,
               'new_currency': self.currency_id.id,
               'journal_id': self.journal_id.id}
        allowed_sale = res_partner.with_context(ctx).browse(
            self.partner_id.id).allowed_sale
        if self.partner_id and not allowed_sale:
            credit_overloaded = res_partner.with_context(ctx).browse(
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

    def create_ir_attachment_facturae(self):
        """Make the Electronic Invoice confirmed and signed automatically"""
        res = super(AccountInvoice, self).create_ir_attachment_facturae()
        if not isinstance(res, dict):
            return res
        attach_obj = self.env['ir.attachment.facturae.mx']
        attach = attach_obj.search([
            ('model_source', '=', self._name), ('id_source', '=', self.id)])[0]

        if not attach.create_ir_attachment_facturae():
            return False

        result = attach.signal_send_customer()
        view_id = self.env.ref('mail.email_compose_message_wizard_form').id
        result.update({
            'views': [(view_id, 'form')],
            'view_id': view_id,
        })
        return result
