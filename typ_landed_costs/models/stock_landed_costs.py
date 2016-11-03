# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import except_orm, ValidationError
import openerp.addons.decimal_precision as dp


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
        default=lambda self:
        self._get_user_default_company(),
        help='Company which this guide belongs to')
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Partner associated to this guide')
    date = fields.Date(
        required=True,
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
    amount_total = fields.Float(
        string='Total',
        digits=dp.get_precision('Account'),
        store=True,
        readonly=True,
        compute='_compute_amount')
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
    landed = fields.Boolean(
        string='Is Landed Cost validated?',
        help='This field is automatically True if the guide belongs to a'
        ' validated Landed Cost document',
        compute='_compute_landed')
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
    invoiced = fields.Boolean(string='Invoiced',
                              help='When the guide has been invoiced, this'
                              ' field is True, otherwise False')
    invoice_id = fields.Many2one('account.invoice', string='Invoice',
                                 help='Refers the invoice related whit'
                                 ' this guide')

    @api.multi
    @api.depends('line_ids.cost')
    def _compute_amount(self):
        for guide in self:
            guide.amount_total = sum(guide.line_ids.mapped('cost'))

    @api.multi
    def _compute_landed(self):
        """Set 'landed' field to True if the Landed Cost document of this guide
        is in Valid state"""
        for guide in self:
            lc = guide.landed_cost_id
            guide.landed = lc and lc.state == 'done'

    @api.model
    def _get_user_default_currency(self):
        """Return the default currency of the current user"""
        return self.env.user.company_id.currency_id

    @api.model
    def _get_user_default_company(self):
        """Return the default company for the current user"""
        return self.env.user.company_id

    @api.multi
    def action_draft(self):
        for guide in self:
            if guide.landed_cost_id:
                raise ValidationError(
                    _("You cannot reset this guide to draft while it is"
                      " associated to a Landed Cost Document:\n\n- %s" %
                      guide.landed_cost_id.name))
            self._cancel_moves()
            guide.state = 'draft'

    @api.model
    def _cancel_moves(self):
        moves = self.move_id
        # First, set the guides as cancelled and detach the move ids
        self.write({'move_id': False})
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this guide was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        # TODO: self._log_event(-1.0, 'Cancel Invoice')
        return True

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
                    _('No Guide Lines!'),
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
            # Pass guide in context in method post: used if you want to get
            # the same
            # account move reference when creating the same guide after a
            # cancelled one:
            move.post()
        # TODO self._log_event()
        return True

    @api.multi
    def compute_guide_totals(self, company_currency, ref, guide_move_lines):
        total = 0
        total_currency = 0
        currency = self.currency_id.with_context(
            date=self.date or fields.Date.context_today(self))
        for line in guide_move_lines:
            line['ref'] = ref
            line['currency_id'] = False
            line['amount_currency'] = False
            if self.currency_id != company_currency:
                line['currency_id'] = currency.id
                line['amount_currency'] = currency.round(line['price'])
                line['price'] = currency.compute(
                    line['price'], company_currency)
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
            'guide_line_id': line.get('guide_line_id', False),
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

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        """Filter list of Journals based on the selected warehouse. If the
        warehouse selected is default for a Sale Team, we filter the list of
        Journals associated to this Sale Team"""
        warehouse = self.warehouse_id.id
        res = {}
        if warehouse:
            journals = self.env['crm.case.section'].search(
                [('default_warehouse', '=', warehouse)]
            ).journal_team_ids.ids
            domain = [('id', 'in', journals)] if journals else []
            if journals:
                res['domain'] = {'journal_id': domain}
        return res

    @api.multi
    def view_accrual(self):
        """Launches a view with the account.move.lines related to the current
        guide"""
        res = []
        for guide in self:
            res += guide.line_ids.ids

        domain = "[('guide_line_id', 'in', \
            [" + ','.join([str(item) for item in res]) + "])]"
        return {
            'domain': domain,
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


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
    def product_stock_account_in(self):
        """Returns the ID for the 'stock_account_input' of the current line
        product"""
        product_tmpl = self.product_id.product_tmpl_id
        accounts = product_tmpl.get_product_accounts(product_tmpl.id)
        return accounts['stock_account_input']

    @api.model
    def move_line_get(self, guide_id):
        guide_brw = self.env['stock.landed.cost.guide'].browse(guide_id)
        res = []
        for line in guide_brw.line_ids:

            debit = self.move_line_get_item(line)
            res.append(debit)

            # Reverse entry line for the input account
            credit = debit.copy()
            credit.update({
                'account_id': line.product_stock_account_in(),
                'price': credit['price'] * -1,
                'guide_line_id': line.id,
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

    @api.multi
    def button_validate(self):
        """Inherited to add a validation message"""
        draft_guides = self.env['stock.landed.cost.guide']
        for landed in self:
            draft_guides += landed.guide_ids.filtered(
                lambda dat: 'draft' in dat.state)
        msj = ""
        for guide in draft_guides:
            msj += _("\n- Check '%s' into '%s'") % (
                guide.name, guide.landed_cost_id.name)
        if draft_guides:
            raise ValidationError(
                _('Only valid guides can be added to a landed cost') + msj)
        return super(StockLandedCost, self).button_validate()

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
                        'split_method': 'by_quantity',
                        'segmentation_cost': 'landed_cost'
                    }))
            if lines:
                landed_cost.update({'cost_lines': lines})
        return res

    def lcost_from_inv_line(self, inv_line):
        """Inherited from stock_landed_cost_average to set default value of
        segmentation_cost field to 'landed_cost'"""
        res = super(StockLandedCost, self). lcost_from_inv_line(inv_line)
        res['segmentation_cost'] = 'landed_cost'
        return res


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    segmentation_cost = fields.Selection(default='landed_cost')
