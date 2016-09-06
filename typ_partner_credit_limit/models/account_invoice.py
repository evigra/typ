# -*- coding: utf-8 -*-

from openerp import models, api, _


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
        self.ensure_one()
        if not self.need_verify_limit_credit():
            return True
        super(AccountInvoice, self).check_limit_credit()

    @api.multi
    def onchange_partner_id(self, types, partner_id, date_invoice=False,
                            payment_term=False, partner_bank_id=False,
                            company_id=False):
        """Show warning message if partner selected has no credit limit.
        """
        res = super(AccountInvoice, self).onchange_partner_id(
            types, partner_id, date_invoice, payment_term, partner_bank_id,
            company_id)
        partner = self.env['res.partner'].browse(partner_id)
        if not partner.allowed_sale:
            warning = {
                'title': _('Warning!'),
                'message': _('The partner selected has the credit closed.'),
            }
            res['warning'] = warning
        return res
