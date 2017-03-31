# coding: utf-8
from __future__ import division
from datetime import datetime, timedelta
from openerp.tools import float_round
from openerp import models, fields, api, tools
from openerp.tools.safe_eval import safe_eval


class CommisionReportsBase(models.Model):

    _name = "commision.reports.base"
    _inherit = ['mail.thread']

    name = fields.Char('Report Title')
    comment_commisions = fields.Text('Comment about Commisions',
                                     help="It will appear just above "
                                     "list of commisions.")
    filter_id = fields.Many2one('ir.filters', 'Filter',
                                domain=[
                                    ('model_id', '=', 'account.invoice.line')],
                                help="Filter should be by date, "
                                "group_by is ignored, the model "
                                "which the filter should belong "
                                "to invoice line")
    filter_inv_id = fields.Many2one('ir.filters', 'Filter',
                                    domain=[
                                        ('model_id', '=', 'account.invoice')],
                                    help="Filter should be by date, "
                                    "group_by is ignored, the model "
                                    "which the filter should belong "
                                    "to invoice line")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], 'Status',
                             default='draft',
                             help='Status of the report')
    invoice = fields.Boolean(help='Used to use filter applied in invoices')
    lines = fields.Boolean('Invoice Lines',
                           help='Used to use filter applied in invoice lines')
    custom = fields.Boolean('Custom Filter',
                            help='Used to specify custom filter and allow '
                            'use the date to search by payments ')
    date_start = fields.Date('Initial Date',
                             help='Date where the range starts')
    date_end = fields.Date('End Date',
                           help='Date where the range ends')
    partner_id = fields.Many2one(
        'res.partner', 'Customer', help='Customer owner of the invoice')
    company_id = fields.Many2one(
        'res.company', 'Company', help='Company which this report belongs to')

    @api.multi
    def go_to_invoice_lines(self):
        """Return to the new invoice lines view with the lines filtered by the
        domain in the filter used in the report
        """
        self.ensure_one()
        view = self.env.ref('typ_commision.view_invoice_line_tree')
        if self.invoice:
            domain = safe_eval(self.filter_inv_id.domain)
            invoices = self.env['account.invoice']._search(domain)
            domain = [('invoice_id', 'in', invoices),
                      ('type', 'in', ('out_invoice', 'out_refund'))]
        elif self.custom:
            domain = []
            domain += (('partner_id', '=', self.partner_id.id)
                       if self.partner_id else ())
            domain += [('date', '>=', self.date_start),
                       ('date', '<=', self.date_end),
                       ('account_id.type', '=', 'receivable'),
                       ('reconcile_id', '!=', False)]
            aml_ids = self.env['account.move.line'].search(domain)
            reconcile = aml_ids.mapped('reconcile_id').mapped(
                'line_id.move_id')
            invoices = self.env['account.invoice'].sudo()._search(
                [
                    '&', '&', '|',
                    ('date_invoice', '>=', self.date_start),
                    ('date_invoice', '<=', self.date_end),
                    ('state', '!=', 'cancel'),
                    ('move_id', 'in', reconcile.ids),
                ])
            domain = [
                ('product_id', '!=', False),
                ('invoice_id', 'in', invoices)]
        else:
            domain = safe_eval(self.filter_id.domain or '[]')
            domain += [
                ('invoice_id.type', 'in', ('out_invoice', 'out_refund'))]
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice.line',
            'name': 'Commission Report',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view.id,
            'domain': domain,
            'context': self.filter_id.context or '{}'}

    @api.multi
    @tools.ormcache(skiparg=1)
    def _get_payment_values(self, inv):
        """Used to get the date and period of a payment related with the
        journal item

        :param inv: Invoice which you want to know its payments
        :type inv: account.invoice()

        :return: Period and date when the invoice was paid
        :rtype: (int, account.period())
        """
        payment = inv.move_id.line_id.filtered(
            lambda a: (
                a.account_id.id ==
                inv.commercial_partner_id.property_account_receivable.id and
                a.reconcile_id.id is not False))
        date = None
        period = None
        if payment:
            line_id = self.env['account.move.line'].search(
                [('id', '!=', payment[0].id),
                 ('reconcile_id', '=', payment[0].reconcile_id.id)],
                order='date DESC',
                limit=1)
            date = line_id.date if line_id else None
            period = line_id.period_id if line_id else None

        return date, period

    @api.multi
    def _get_journal_values(self, line, inv):
        """Get the values related with the line in the journal items, this to
        compute accounting margin and the rate used at the momento to create
        the journal item
        :param line: Line of the invoice
        :type line: account.invoice.line()

        :return: The needed values to update the lines
        :rtpe: dict
        """
        vals = {}
        items = inv.move_id.line_id.filtered(
            lambda a: (a.product_id.id == line.product_id.id and
                       a.quantity == line.quantity))
        exp_acc_id = (
            line.product_id.property_account_expense.id or
            line.product_id.categ_id.property_account_expense_categ.id)
        expense = 0
        income = 0
        for item in items:
            expense = ((item.credit or item.debit)
                       if item.account_id.id == exp_acc_id else expense)
            income = (((item.credit or item.debit), item.amount_currency)
                      if item.account_id.id == line.account_id.id else income)
        amount_currency = income and income[1]
        income = income and income[0]
        rate = 1/(abs(amount_currency)/income) if amount_currency < 0 else 1
        margin = (
            (float_round((income - expense),
                         inv.currency_id.rounding) / income) * 100
            if income > 0 else 0)

        date, period = self._get_payment_values(inv)

        vals.update(
            {'rate': rate,
             'margin': margin,
             'payment_date': date,
             'period_id': period.id if period else None,
             'cost': expense}
        )
        return vals

    @api.multi
    @tools.ormcache(skiparg=1)
    def _get_stock_card_product(self, product_id):
        """Method used to get the stock_card value for product in the
        invoice

        :param product_id: Product used to obtain its stock_card
        :type product_id: int

        :return: Historical stock_card
        :rtype: pandas.Dataframe()
        """
        stock_card = self.env['stock.card.product']
        costs = stock_card.get_stock_card_date_range(product_id)
        return costs

    @api.multi
    @tools.ormcache(skiparg=1)
    def _get_invoice_values(self, inv):
        """Get the invoice value to use in report and avoid request them in
        each line

        :param inv: Invoice in the range of day in the report
        :type inv: account.invoice()

        :return: Values needed extracted from the invoice
        :rtype: dict
        """
        vals = {
            'user_id': inv.user_id.id or None,
            'puser_id': inv.partner_id.user_id.id or None,
            'section_id': (inv.section_id.id or
                           inv.user_id.default_section_id.id or None),
            'date_invoice': inv.date_invoice or None,
            'date_due': inv.date_due or None,
            'state': inv.state,
            'inv_name': inv.number or None,
            'type_payment_term': inv.type_payment_term or None,
            'currency': inv.currency_id.id or None,
            'type': inv.type,
            'credit_note_type': inv.credit_note_type or None,
            'parent_invoice_id': inv.parent_invoice_id.id or None,
        }

        return vals

    @api.multi
    @tools.ormcache(skiparg=1)
    def _get_date_to_use(self, date_invoice):
        """Used to get the date plus one day

        :param date_invoice: Date when the invoice was created
        :type date_invoice: str

        :return: date plus one day to compute the cost
        :rtype: str
        """
        date_to_use = (
            datetime.strptime(date_invoice,
                              '%Y-%m-%d') + timedelta(days=1)
            if date_invoice else False)
        date_to_use = date_to_use.strftime(
            '%Y-%m-%d') if date_to_use else ''

        return date_to_use

    @api.multi
    def execute_update(self, domain=None):
        """This method generate the query to update the new values in the
        invoice_line

        :param domain: Domain used to search the lines
        :type domain: list of tuple

        """
        line_obj = self.env['account.invoice.line'].sudo()
        lines = line_obj._search(domain)
        if not lines:
            return True
        for line in lines:
            line = line_obj.browse(line)
            inv = line.invoice_id
            costs = self._get_stock_card_product(line.product_id.id)
            date_to_use = self._get_date_to_use(inv.validation_date or
                                                inv.date_invoice)
            average = (
                costs['average'][:date_to_use][-1]
                if date_to_use and costs.empty is False and
                costs['average'][:date_to_use].empty is False else 0.0)
            journal_values = self._get_journal_values(line, inv)
            vals = self._get_invoice_values(inv)
            vals.update({
                'sale_margin': journal_values.get('margin'),
                'payment_date': journal_values.get('payment_date'),
                'period_id': journal_values.get('period_id'),
                'categ_id': line.product_id.categ_id.id or None,
                'currency_rate': journal_values.get('rate'),
                'price_cost': journal_values.get('cost'),
                'id': line.id,
                'cost_transaction': average * line.quantity,

            })
            self._cr.execute(
                '''
                UPDATE
                    account_invoice_line
                SET
                    sale_margin=%(sale_margin)s,
                    user_id=%(user_id)s,
                    puser_id=%(puser_id)s,
                    section_id=%(section_id)s,
                    date_invoice=%(date_invoice)s,
                    date_due=%(date_due)s,
                    payment_date=%(payment_date)s,
                    period_id=%(period_id)s,
                    state=%(state)s,
                    inv_name=%(inv_name)s,
                    type_payment_term=%(type_payment_term)s,
                    categ_id=%(categ_id)s,
                    currency=%(currency)s,
                    currency_rate=%(currency_rate)s,
                    price_cost=%(price_cost)s,
                    type=%(type)s,
                    credit_note_type=%(credit_note_type)s,
                    parent_invoice_id=%(parent_invoice_id)s,
                    cost_transaction=%(cost_transaction)s
                WHERE
                    id=%(id)s
                             ''', vals)

    @api.multi
    def fill_required_fields(self):
        """Get and update the new values added in the invoice lines to compute
        the commisions for salesman
        """
        self.ensure_one()
        if self.invoice:
            domain = safe_eval(self.filter_inv_id.domain)
            invoices = self.env['account.invoice'].sudo()._search(domain)
            domain = [('invoice_id', 'in', invoices),
                      ('period_id', '=', False),
                      ('product_id', '!=', False)]
        elif self.custom:
            domain = []
            domain += (('partner_id', '=', self.partner_id.id)
                       if self.partner_id else ())
            domain += [('date', '>=', self.date_start),
                       ('date', '<=', self.date_end),
                       ('account_id.type', '=', 'receivable'),
                       ('reconcile_id', '!=', False)]
            aml_ids = self.env['account.move.line'].search(domain)
            reconcile = aml_ids.mapped('reconcile_id').mapped(
                'line_id.move_id')
            invoices = self.env['account.invoice'].sudo()._search(
                [
                    '&', '&', '|',
                    ('date_invoice', '>=', self.date_start),
                    ('date_invoice', '<=', self.date_end),
                    ('state', '!=', 'cancel'),
                    ('move_id', 'in', reconcile.ids),
                ])
            domain = [
                ('product_id', '!=', False),
                ('period_id', '=', False),
                ('invoice_id', 'in', invoices)]
        else:
            domain = safe_eval(self.filter_id.domain or '[]')
            domain += [
                ('invoice_id.type', 'in', ('out_invoice', 'out_refund')),
                ('product_id', '!=', False),
                ('period_id', '=', False)]

        self.execute_update(domain)
