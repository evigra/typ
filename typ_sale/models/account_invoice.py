
from openerp import api, fields, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    type_payment_term = fields.Selection(
        [('credit', 'Credit'), ('cash', 'Cash'),
         ('postdated_check', 'Postdated check')], default='credit')

    @api.onchange('type_payment_term', 'partner_id')
    def get_payment_term(self):
        """Get payment term depends on type payment term in invoice register.
        """
        acc_payment_term_obj = self.env['account.payment.term']
        self = self._context.get('res_id') or self
        if not self.partner_id:
            return
        immediate_payment = self.env.ref(
            'account.account_payment_term_immediate')
        self.payment_term_id = self.partner_id.property_payment_term_id.id
        pos_order = self.env['pos.order'].search([
            ('invoice_id', '=', self.id)])
        if pos_order and (not self.payment_term_id or
                          self.payment_term_id.payment_type != 'cash' or
                          self.type_payment_term != 'cash'):
            self.payment_term_id = immediate_payment
            self.type_payment_term = 'cash'
            return
        if self.type_payment_term in ('cash', 'postdated_check'):
            payment_term = acc_payment_term_obj.search([]).filtered(
                lambda dat: dat.payment_type == 'cash')
            self.payment_term_id = payment_term[0] if payment_term else False

        if self.type_payment_term == 'credit' and (
                not self.payment_term_id or
                self.payment_term_id.payment_type == 'cash'):
            self.type_payment_term = 'cash'
            if not self.payment_term_id:
                self.payment_term_id = immediate_payment

        elif self.type_payment_term in ('cash', 'postdated_check') and \
                self.payment_term_id.payment_type == 'credit':
            self.type_payment_term = 'credit'
