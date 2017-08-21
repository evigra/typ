# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    credit_note_type = fields.Selection(
        [('error', 'Error'),
         ('advance', 'Advance'),
         ('return', 'Return'),
         ('warranty', 'Warranty'),
         ('gift', 'Gift'),
         ('rebilling', 'Rebilling'),
         ('financing', 'Financing'),
         ('other', 'Other')],
        'Type',
        help='Used to identify the reason of this credit note')

    parent_invoice_id = fields.Many2one('account.invoice', 'Invoice',
                                        help='Parent invoice that '
                                        'generates this credit note',
                                        copy=False)


class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'

    credit_note_type = fields.Selection(
        [('error', 'Error'),
         ('advance', 'Advance'),
         ('return', 'Return'),
         ('warranty', 'Warranty'),
         ('gift', 'Gift'),
         ('rebilling', 'Rebilling'),
         ('financing', 'Financing'),
         ('other', 'Other')],
        help='Used to identify the reason of this credit note')

    parent_invoice_id = fields.Many2one('account.invoice', 'Invoice',
                                        help='Parent invoice that '
                                        'generates this credit note',
                                        copy=False)
    sale_margin = fields.Float('Margin',
                               help="Margin of the product "
                               "at the moment to sale", copy=False)
    user_id = fields.Many2one('res.users', 'Salesperson',
                              help='Salesman in the sale order', copy=False)
    puser_id = fields.Many2one('res.users', 'Customer Salesperson',
                               readonly=True,
                               help='Salesman in the partner', copy=False)
    section_id = fields.Many2one('crm.case.section', 'Sales Team',
                                 help='Salesteam of the salesman '
                                 'for this order', copy=False)
    date_invoice = fields.Date(string='Invoice Date',
                               readonly=True, help="Date in the invoice",
                               copy=False)
    date_due = fields.Date(string='Due Date',
                           help="Date due of the invoice", copy=False)
    payment_date = fields.Date(help="Date of the last payment of the invoice",
                               copy=False)
    currency = fields.Many2one('res.currency', copy=False)
    period_id = fields.Many2one('account.period',
                                'Payment Period',
                                help="Period of the last payment", copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
        ], string='Status', copy=False)
    inv_name = fields.Char(string='Invoice', copy=False)
    type_payment_term = fields.Selection(
        [('credit', 'Credit'), ('cash', 'Cash'),
         ('postdated_check', 'Postdated check')], default='credit',
        copy=False)
    categ_id = fields.Many2one('product.category', 'Product Category',
                               readonly=True, help='Category of the '
                               'product in the order', copy=False)
    currency_rate = fields.Float('Rate',
                                 help='Rate used to compute '
                                 'the price in the invoice', copy=False)
    price_cost = fields.Float('Cost',
                              help='Cost of the product at '
                              'the moment of the sale', copy=False)
    cost_transaction = fields.Float(
        'Transaction Cost',
        help='Real cost of the transaction. This cost is computed considering '
        'landed costs added after the validation of this order but '
        'created before this', copy=False)
    type = fields.Selection([
        ('out_invoice', 'Customer Invoice'),
        ('in_invoice', 'Supplier Invoice'),
        ('out_refund', 'Customer Refund'),
        ('in_refund', 'Supplier Refund'),
        ], copy=False)
    product_default_code = fields.Char(string='Product Internal Reference',
                                       copy=False)
    partner_importance = fields.Selection([
        ('AA', 'AA'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('X', 'X'),
        ('NEW', 'NEW'),
        ('NEGOTIATION', 'NEGOTIATION'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED')], copy=False)
    partner_potential_import = fields.Selection([
        ('AA', 'AA'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('X', 'X'),
        ('NEW', 'NEW'),
        ('NEGOTIATION', 'NEGOTIATION'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED')], copy=False)
    partner_business_act = fields.Selection([
        ('CONTRACTORS', 'CON'),
        ('COMPANY', 'COM'),
        ('WHOLESALERS', 'WHO'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('PUBLIC', 'PUBLIC')], copy=False)
    partner_type = fields.Selection([
        ('OC', 'OC'),
        ('NC', 'NC'),
        ('PC', 'PC'),
        ('RC', 'RC'),
        ('ESP', 'ESP'),
        ('FSC', 'FSC'),
        ('SUP', 'SUP'),
        ('BOT', 'BOT'),
        ('OTH', 'OTH'),
        ('WHC', 'WHC'),
        ('WW', 'WW'),
        ('WI', 'WI'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('PUBLIC', 'PUBLIC')], copy=False)
    partner_dealer = fields.Selection([
        ('PD', 'PD'),
        ('AD', 'AD'),
        ('SD', 'SD')], copy=False)
    partner_region = fields.Selection([
        ('NORTHWEST', 'NORTHWEST'),
        ('WEST', 'WEST'),
        ('CENTER', 'CENTER'),
        ('NORTHEAST', 'NORTHEAST'),
        ('SOUTHEAST', 'SOUTHEAST'),
        ('SOUTH', 'SOUTH')], copy=False)
