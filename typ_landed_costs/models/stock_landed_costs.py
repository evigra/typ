# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm


class StockLandedGuides (models.Model):
    _name = 'stock.landed.cost.guide'
    name = fields.Char(
        required=True,
        help='Name to identify the guide',
        readonly=True,
        states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        change_default=True,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Company which this guide belongs to')
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Partner associated to this guide')
    date = fields.Date(
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Date of the guide')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda self:
        self._get_user_default_currency(),
        help='Currency used for this guide')
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Warehouse which this guide belongs to')
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Journal used for this guide')
    landed_cost_id = fields.Many2one(
        'stock.landed.cost',
        string='Landed Cost',
        help='Landed cost document where this guide is added',
        readonly=True)
    line_ids = fields.One2many(
        'stock.landed.cost.guide.line',
        'guide_id',
        string='Guide Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Product lines associated to this guide')
    reference = fields.Char(
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Reference code for this guide')
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        index=True,
        ondelete='restrict',
        copy=False,
        help="Link to the automatically generated Journal Items.")
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        copy=False,
        help="Guide period",
        readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('valid', 'Valid')],
        string='Status',
        default='draft',
        help='Guide status')

    @api.model
    def _get_user_default_currency(self):
        """Return the default currency of the current user"""
        return self.env.user.company_id.currency_id

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_valid(self):
        self.action_move_create()
        self.state = 'valid'

    @api.multi
    def action_move_create(self):
        """Creates guide related financial move lines"""
        account_move = self.env['account.move']

        for guide_brw in self:
            if not guide_brw.journal_id.sequence_id:
                raise except_orm(
                    _('Error!'),
                    _('Please define sequence on the journal related to this'
                      ' guide.'))
            if not guide_brw.line_ids:
                raise except_orm(
                    _('No Invoice Lines!'),
                    _('Please create some guide lines.'))
            if guide_brw.move_id:
                continue
            ctx = dict(self._context, lang=guide_brw.partner_id.lang)
            journal = guide_brw.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(
                    _('User Error!'),
                    _('You cannot create a guide on a centralized journal.'
                      ' Uncheck the centralized counterpart box in the related'
                      ' journal from the configuration menu.'))

            if not guide_brw.date:
                guide_brw.with_context(ctx).write(
                    {'date': fields.Date.context_today(self)})
            date = guide_brw.date

            ref = guide_brw.reference or guide_brw.name,
            company_currency = guide_brw.company_id.currency_id
            gml = self.env['stock.landed.cost.guide.line'].move_line_get(
                self.id)

            # TODO: Review to implement multi currency with @hbto
            # diff_currency = guide_brw.currency_id != company_currency
            # create one move line for the total and possibly adjust the other
            # lines amount
            # total, total_currency, gml = guide_brw.with_context(
            #     ctx).compute_guide_totals(company_currency, ref, gml)
            gml = guide_brw.with_context(
                ctx).compute_guide_totals(company_currency, ref, gml)[2]

            part = self.env['res.partner']._find_accounting_partner(
                guide_brw.partner_id)

            line = [(0, 0,
                     self.line_get_convert(l, part.id, date)) for l in gml]
            line = guide_brw.finalize_guide_move_lines(line)
            move_vals = {
                'ref': guide_brw.reference or guide_brw.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': date,
                'company_id': guide_brw.company_id.id,
            }
            ctx['company_id'] = guide_brw.company_id.id
            period = guide_brw.period_id.with_context(ctx).find(date)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)

            # make the guide point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
            }
            guide_brw.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get
            # the same
            # account move reference when creating the same invoice after a
            # cancelled one:
            # TODO: move.post()
        # TODO self._log_event()
        return True

    @api.multi
    def compute_guide_totals(self, company_currency, ref, guide_move_lines):
        total = 0
        total_currency = 0
        for line in guide_move_lines:
            if self.currency_id != company_currency:
                # TODO: Review to implement multi currency with @hbto
                pass
                # currency = self.currency_id.with_context(
                #     date=self.date or fields.Date.context_today(self))
                # line['currency_id'] = currency.id
                # line['amount_currency'] = currency.round(line['price'])
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
            line['ref'] = ref
        return total, total_currency, guide_move_lines

    @api.model
    def line_get_convert(self, line, part, date):
        return {
            'date_maturity': line.get('date_maturity', False),
            'partner_id': part,
            'name': line['name'][:64],
            'date': date,
            'debit': line['price'] > 0 and line['price'],
            'credit': line['price'] < 0 and -line['price'],
            'account_id': line['account_id'],
            'analytic_lines': line.get('analytic_lines', []),
            'amount_currency': line['price'] > 0 and abs(
                line.get('amount_currency', False)) or -abs(
                    line.get('amount_currency', False)),
            'currency_id': line.get('currency_id', False),
            'tax_code_id': line.get('tax_code_id', False),
            'tax_amount': line.get('tax_amount', False),
            'ref': line.get('ref', False),
            'quantity': line.get('quantity', 1.00),
            'product_id': line.get('product_id', False),
            'product_uom_id': line.get('uos_id', False),
            'analytic_account_id': line.get('account_analytic_id', False),
        }

    @api.multi
    def finalize_guide_move_lines(self, move_lines):
        """ finalize_guide_move_lines(move_lines) -> move_lines

            Hook method to be overridden in additional modules to verify and
            possibly alter the move lines to be created by a guide, for
            special cases.
            :param move_lines: list of dictionaries with the account.move.lines
            (as for create())
            :return: the (possibly updated) final move_lines to create for this
            guide
        """
        return move_lines


class StockLandedGuidesLine (models.Model):
    _name = 'stock.landed.cost.guide.line'
    guide_id = fields.Many2one(
        'stock.landed.cost.guide',
        help='Guide which this line belongs to')
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Product associated to this line')
    cost = fields.Float(help='Cost of the operation on this line')
    freight_type = fields.Selection(
        [('others', 'Freight - Others'),
         ('purchases', 'Freight - Purchases'),
         ('transfers', 'Freight - Transfers'),
         ('sales', 'Freight - Sales'),
         ('services', 'Services')],
        help='Freight type of this operation'
        )

    @api.model
    def move_line_get(self, guide_id):
        guide_brw = self.env['stock.landed.cost.guide'].browse(guide_id)
        res = []
        for line in guide_brw.line_ids:
            product_tmpl = line.product_id.product_tmpl_id
            p_accounts = product_tmpl.get_product_accounts(product_tmpl.id)

            debit = self.move_line_get_item(line)
            debit['guidel_id'] = line.id
            res.append(debit)

            # Reverse entry line for the input account
            credit = debit.copy()
            credit.update({
                'account_id': p_accounts['stock_account_input'],
                'price': credit['price'] * -1,
            })
            res.append(credit)
        return res

    @api.model
    def move_line_get_item(self, line):
        account = line.product_id.categ_id.property_account_expense_categ
        return {
            'type': 'src',
            'name': line.product_id.name.split('\n')[0][:64],
            'price_unit': line.cost,
            'account_id': account.id,
            'price': line.cost,
            'product_id': line.product_id.id,
            'uos_id': line.product_id.uos_id.id,
        }


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    guide_ids = fields.One2many(
        'stock.landed.cost.guide',
        'landed_cost_id',
        string='Guides',
        help='Guides which contain items to be used as landed costs',
        copy=False)

    @api.onchange('invoice_ids', 'guide_ids')
    def onchange_invoice_ids(self):
        """Inherited from stock.landed.costs in oder to add the logic necessary
        to update the list with the elements extracted when guides are
        added/removed"""
        # We first load products from invoices calling super()
        res = super(StockLandedCost, self).onchange_invoice_ids()
        company_currency = self.env.user.company_id.currency_id
        for landed_cost in self:
            lines = landed_cost.cost_lines.mapped('id')
            # Now we load the products present in guides
            for guide in landed_cost.guide_ids:
                for line in guide.line_ids:
                    product = line.product_id
                    account = product.categ_id.property_account_expense_categ
                    diff_currency = guide.currency_id != company_currency
                    cost = line.cost
                    if diff_currency:
                        cost = guide.currency_id.with_context(
                            date=guide.date).compute(
                                line.cost, company_currency)
                    lines.append((0, False, {
                        'name': product.name,
                        'account_id': account,
                        'product_id': product.id,
                        'price_unit': cost,
                        'split_method': 'by_quantity'
                    }))
            if lines:
                landed_cost.update({'cost_lines': lines})
        return res
