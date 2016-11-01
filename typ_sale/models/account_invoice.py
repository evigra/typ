# coding: utf-8

from openerp import api, fields, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    type_payment_term = fields.Selection(
        [('credit', 'Credit'), ('cash', 'Cash'),
         ('postdated_check', 'Postdated check')], default='credit',
        string='Type payment term')

    @api.onchange('type_payment_term', 'partner_id')
    def get_payment_term(self):
        """Get payment term depends on type payment term in invoice register.
        """
        acc_payment_term_obj = self.env['account.payment.term']
        if self.partner_id:
            if self.type_payment_term in ('cash', 'postdated_check'):
                for payment_term in \
                        acc_payment_term_obj.search([]):
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
