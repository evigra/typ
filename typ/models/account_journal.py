# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_mx_edi_payment_method_id = fields.Many2one(
        'l10n_mx_edi.payment.method',
        string="Payment Method",
        help='This payment method will be used by default in the related '
        'documents (invoices, payments, and bank statements).')
