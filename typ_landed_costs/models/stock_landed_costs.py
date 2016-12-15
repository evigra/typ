# -*- coding: utf-8 -*-

from __future__ import division
from datetime import timedelta
from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError
from openerp.exceptions import except_orm, ValidationError
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero


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
    account_move_name = fields.Char(
        readonly=True,
        help='Stores the name of the Journal Entry the first time the Guide is'
        ' validated, so if the user cancel or reset the guide and then create'
        ' it again, it will not create a new Journal Entry Sequence, it will'
        ' use always the same'
    )
    period_id = fields.Many2one(
        'account.period',
        string='Period',
        copy=False,
        help="Guide period",
        readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('valid', 'Valid'),
         ('cancel', 'Cancelled')],
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
    def unlink(self):
        details = ""
        for guide in self:
            if guide.account_move_name:
                details += _("Guide '%s' cannot be removed when it is/was"
                             " validated\n") % (guide.name)
        if details:
            msg = _('You are trying to delete guides you can not delete:'
                    '\n\n%s\nPlease solve this errors before continue.'
                    ) % details
            raise ValidationError(msg)
        return super(StockLandedGuides, self).unlink()

    @api.multi
    def action_cancel(self):
        """Move the guide to Cancelled state, it's used when the Guide is
        associated to a Landed Cost Document because in this condition the
        guide can not be removed"""
        for guide in self:
            self._cancel_moves()
            guide.state = 'cancel'

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
        if not self.move_id:
            return True
        moves = self.move_id
        # First, detach the move ids
        self.write({'move_id': False})
        # second, invalidate the move(s)
        moves.button_cancel()
        # delete the move this guide was pointing to
        # Note that the corresponding move_lines and move_reconciles
        # will be automatically deleted too
        moves.unlink()
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
            if guide_brw.account_move_name:
                move_vals['name'] = guide_brw.account_move_name
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
            guide_brw.account_move_name = move.name
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

    exchange_landed_ids = fields.Many2many(
        'stock.landed.cost',
        'adjust_landed_import_landed_rel'
        'main_landed_id',
        'adjust_landed_id',
        string='Exchange Differential Adjust',
        help='Landed created to adjust '
        'the cost of the product by '
        'exchange differential')

    def adjust_exchange_rate(method):
        """Method used like decorator to choose method depending of the object
        sent at the moment to do the adjustments
        """
        def wrapper(self, *args, **kwargs):
            model = args and args[0]
            move_lines = self.env['stock.move']
            vals = {
                'stock.picking': ('move_lines',),
                'account.invoice': ('invoice_line', 'move_id'),
                'account.move': ('line_id', 'sm_id'),
                'account.move.line': ('sm_id', 0, 0),
                'stock.move': ()
            }
            if model._name not in vals:
                raise UserError('Not implement yet for this model %s'
                                % model._name)
            val = vals[model._name]
            move_lines += (
                len(val) == 0 and model or
                len(val) == 1 and model[val[0]] or
                len(val) == 2 and model[val[0]].mapped(val[1]) or
                len(val) == 3 and model.mapped(val[0])
                )

            return method(self, move_lines, args[1])
        return wrapper

    @api.model
    def _get_result_diff_rate(self, line, date, days=0):
        """When the partner is foreign is needed compute the debit of the
        journal items but using a rate of a date ago

        :param move_lines: Move that we need to adjust to set the correct cost
        in the products with the real rate
        :type move_lines: recordset
        :param date: Date to compute the real cost with the correct rate
        :type date: str
        :param days: Number of day that we need to reduce the date sent to
        compute the rate
        :type days: int
        :return The new total compute with the needed date
        :rtype float
        """
        new_date = (fields.Date.from_string(date) -
                    timedelta(days=days))
        currency_obj = self.env['res.currency']
        currency_obj = currency_obj.with_context({'date': new_date})
        from_currency = line.purchase_line_id.order_id.currency_id
        to_currency = self.env.user.company_id.currency_id
        price_unit = (line.purchase_line_id.price_unit * line.product_qty)
        new_total = (line.product_id and price_unit and
                     currency_obj._compute(from_currency, to_currency,
                                           price_unit) or 0)
        return new_total

    @api.model
    def _get_landed_values(self, diff, picking, journal, date):
        """Generate dict with the values needed for create the landed to adjust costs

        :param picking: Picking that generated the invoice
        :type picking: recordset
        :param diff: Value to adjust
        :type diff: float
        :param date: Date of the document to create
        :type date: str

        :return Values for the new landed
        :rtype dict
        """
        product = self.env.ref('typ_landed_costs.'
                               'landed_exchange_differential_product')
        account = (diff > 0 and
                   self.env.user.company_id.
                   income_currency_exchange_account_id or
                   self.env.user.company_id.
                   expense_currency_exchange_account_id)
        if not account:
            raise UserError(_('Insufficient Configuration!'),
                            _("You should configure the 'Exchange Rate "
                              "Account' in the accounting settings, "
                              "to manage automatically the booking "
                              "of accounting entries related to "
                              "differences between exchange rates."))
        cost_line = {
            'product_id': product.id,
            'name': product.name,
            'account_id': account.id,
            'split_method': 'by_current_cost_price',
            'price_unit': diff,
            'segmentation_cost': 'material_cost'

        }
        values = {
            'date': date,
            'account_journal_id': journal,
            'picking_ids': [(4, picking.id)],
            'cost_lines': [(0, 0,
                            cost_line)]
        }
        return values

    @adjust_exchange_rate
    @api.model
    def adjust_cost_for_exchange_differential(self, move_lines, date):
        """Overwritten to create a new landed to update the valuation of the
        products using the rate according to the date invoice.
        If the partner is foreign the date used will be a day before invoice
        data at the moment to validate it

        :return The landed created to adjust the costs
        :rtype stock.landed.cost()
        """
        total_in_move = 0
        diff = 0
        picking = move_lines and move_lines[0].picking_id
        filtered_moves = move_lines.filtered(lambda a:
                                             a.product_id.
                                             cost_method == 'average' and
                                             a.product_id.
                                             valuation == 'real_time')
        for line in filtered_moves:
            aml = line.aml_all_ids[0]
            total_in_move += (aml.debit or aml.credit)
            diff += self._get_result_diff_rate(line, date)

        total_diff = (diff - total_in_move)

        if not total_diff:
            return self.env['stock.landed.cost']

        journal = aml.journal_id.section_id.journal_landed_id.id
        landed_values = self._get_landed_values(total_diff,
                                                picking, journal, date)
        landed_id = self.create(landed_values)
        landed_id.compute_landed_cost()
        landed_id.button_validate()

        return landed_id

    @api.model
    def _get_discrete_values(self, line_id, diff):
        return {
            'move_id': line_id.move_id.id,
            'cost': diff,
            'segmentation_cost': line_id.cost_line_id.segmentation_cost}

    @api.model
    def create_discrete_quant(self, line_id, diff):
        discrete_obj = self.env['stock.discrete']
        vals = self._get_discrete_values(line_id, diff)
        discrete_obj.create(vals)

    @api.multi
    def get_valuation_lines(self, picking_ids=None):
        """It returns product valuations based on picking's moves
        """
        picking_obj = self.env['stock.picking']
        lines = []
        if not picking_ids and not self.move_ids:
            return lines

        # NOTE: Now it is valid for all costing methods available
        move_ids = [
            move_id
            for picking in picking_obj.browse(picking_ids)
            for move_id in picking.move_lines
            if move_id.product_id.valuation == 'real_time'
        ]

        move_ids += [
            move_id
            for move_id in self.move_ids
            if move_id.product_id.valuation == 'real_time'
        ]

        for move in move_ids:
            quants = [quant for quant in move.quant_ids]
            ds_obj = self.env['stock.discrete']
            for qnt in quants:
                for move2 in qnt.history_ids:
                    if move2.date > move.date:
                        continue
                    if move2.discrete_ids:
                        ds_obj += move2.discrete_ids
            # /!\ NOTE: Normalize this computation
            total_cost = sum([
                sd.cost * move.product_qty for sd in set(ds_obj)])

            # total_qty = move.product_qty
            weight = move.product_id and \
                move.product_id.weight * move.product_qty
            volume = move.product_id and \
                move.product_id.volume * move.product_qty
            for quant in move.quant_ids:
                total_cost += quant.cost * quant.qty
            vals = dict(
                product_id=move.product_id.id,
                move_id=move.id,
                quantity=move.product_uom_qty,
                former_cost=total_cost,
                weight=weight,
                volume=volume,
                picking_id=move.picking_id.id)
            lines.append(vals)
        if not lines:
            raise except_orm(
                _('Error!'),
                _('The selected picking does not contain any move that would '
                  'be impacted by landed costs. Landed costs are only possible'
                  ' for products configured in real time valuation. Please '
                  'make sure it is the case, or you selected the correct '
                  'picking.'))
        return lines

    @api.multi
    def button_validate_segmentation(self):
        self.ensure_one()
        quant_obj = self.env['stock.quant']
        # ctx = dict(self._context)

        for cost in self:
            if cost.state != 'draft':
                raise UserError(
                    _('Only draft landed costs can be validated'))
            if not cost.valuation_adjustment_lines or \
                    not self._check_sum(cost):
                raise UserError(
                    _('You cannot validate a landed cost which has no valid '
                      'valuation adjustments lines. Did you click on '
                      'Compute?'))

            if not all([cl.segmentation_cost for cl in cost.cost_lines]):
                raise UserError(
                    _('Please fill the segmentation field in Cost Lines'))

            quant_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id or \
                        line.move_id.location_id.usage == 'internal':
                    continue

                create = False
                if line.move_id.location_id.usage not in (
                        'supplier', 'inventory', 'production'):
                    create = True

                segment = line.cost_line_id.segmentation_cost
                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit

                if create:
                    continue

                for quant in line.move_id.quant_ids:
                    if quant.id not in quant_dict:
                        quant_dict[quant.id] = {}
                        quant_dict[quant.id][segment] = getattr(
                            quant, segment) + diff
                    else:
                        if segment not in quant_dict[quant.id]:
                            quant_dict[quant.id][segment] = getattr(
                                quant, segment) + diff
                        else:
                            quant_dict[quant.id][segment] += diff

            for key, pair in quant_dict.items():
                quant_obj.sudo().browse(key).write(pair)

    @api.multi
    # disable=zip-builtin-not-iterating, too-complex
    # pylint: disable=all
    def button_validate(self):
        """Inherited to add a validation message"""
        self.ensure_one()
        precision_obj = self.pool.get('decimal.precision').precision_get(
            self._cr, self._uid, 'Account')
        quant_obj = self.env['stock.quant']
        template_obj = self.pool.get('product.template')
        scp_obj = self.env['stock.card.product']
        get_average = scp_obj.get_average
        stock_card_move_get = scp_obj._stock_card_move_get
        draft_guides = self.env['stock.landed.cost.guide']
        ctx = dict(self._context)

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

        self.button_validate_segmentation()

        for cost in self:
            if cost.state != 'draft':
                raise UserError(
                    _('Only draft landed costs can be validated'))
            if not cost.valuation_adjustment_lines or \
                    not self._check_sum(cost):
                raise UserError(
                    _('You cannot validate a landed cost which has no valid '
                      'valuation adjustments lines. Did you click on '
                      'Compute?'))

            move_id = self._model._create_account_move(
                self._cr, self._uid, cost, context=ctx)
            prod_dict = {}
            init_avg = {}
            first_lines = {}
            first_card = {}
            last_lines = {}
            prod_qty = {}
            acc_prod = {}
            quant_dict = {}
            for line in cost.valuation_adjustment_lines:
                if not line.move_id or \
                        line.move_id.location_id.usage == 'internal':
                    continue

                create = False
                if line.move_id.location_id.usage not in (
                        'supplier', 'inventory', 'production'):
                    create = True

                product_id = line.product_id

                if product_id.id not in acc_prod:
                    acc_prod[product_id.id] = \
                        template_obj.get_product_accounts(
                        self._cr, self._uid, product_id.product_tmpl_id.id,
                        context=ctx)

                if product_id.cost_method == 'standard':
                    self._create_standard_deviation_entries(
                        line, move_id, acc_prod)
                    continue

                if product_id.cost_method == 'average':
                    if product_id.id not in prod_dict:
                        first_card = stock_card_move_get(product_id.id)
                        prod_dict[product_id.id] = get_average(first_card)
                        first_lines[product_id.id] = first_card['res']
                        init_avg[product_id.id] = product_id.standard_price
                        prod_qty[product_id.id] = first_card['product_qty']

                per_unit = line.final_cost / line.quantity
                diff = per_unit - line.former_cost_per_unit
                quants = [quant for quant in line.move_id.quant_ids]
                if not create:
                    for quant in quants:
                        if quant.id not in quant_dict:
                            quant_dict[quant.id] = quant.cost + diff
                        else:
                            quant_dict[quant.id] += diff
                else:
                    self.create_discrete_quant(line, diff)

                qty_out = 0
                for quant in line.move_id.quant_ids:
                    if quant.location_id.usage != 'internal':
                        qty_out += quant.qty

                if product_id.cost_method == 'average':
                    # /!\ NOTE: Inventory valuation
                    self._create_landed_accounting_entries(
                        line, move_id, 0.0, acc_prod)

                if product_id.cost_method == 'real':
                    self._create_landed_accounting_entries(
                        line, move_id, qty_out, acc_prod)

            for key, value in quant_dict.items():
                quant_obj.sudo().browse(key).write(
                    {'cost': value})

            # /!\ NOTE: This new update is taken out of for loop to improve
            # performance
            for prod_id in prod_dict:
                last_card = stock_card_move_get(prod_id)
                prod_dict[prod_id] = get_average(last_card)
                last_lines[prod_id] = last_card['res']

            # /!\ NOTE: COGS computation
            # NOTE: After adding value to product with landing cost products
            # with costing method `average` need to be check in order to
            # find out the change in COGS in case of sales were performed prior
            # to landing costs
            to_cogs = {}
            for prod_id in prod_dict:
                to_cogs[prod_id] = zip(
                    first_lines[prod_id], last_lines[prod_id])
            for prod_id in to_cogs:
                fst_avg = 0.0
                lst_avg = 0.0
                ini_avg = init_avg[prod_id]
                diff = 0.0
                for tpl in to_cogs[prod_id]:
                    first_line = tpl[0]
                    last_line = tpl[1]
                    fst_avg = first_line['average']
                    lst_avg = last_line['average']
                    if first_line['qty'] >= 0:
                        # /!\ TODO: This is not true for devolutions
                        continue

                    # NOTE: Rounding problems could arise here, this needs to
                    # be checked
                    diff += (lst_avg - fst_avg) * abs(first_line['qty'])
                if not float_is_zero(diff, precision_obj):
                    self._create_cogs_accounting_entries(
                        prod_id, move_id, diff, acc_prod)

                # TODO: Compute deviation
                diff = 0.0
                if prod_qty[prod_id] and fst_avg != ini_avg and \
                        lst_avg != ini_avg:
                    diff = (fst_avg - ini_avg) * prod_qty[prod_id]
                    if not float_is_zero(diff, precision_obj):
                        self._create_deviation_accounting_entries(
                            move_id, prod_id, diff, acc_prod)

            # TODO: Write latest value for average
            cost.compute_average_cost(prod_dict)

            cost.write(
                {'state': 'done', 'account_move_id': move_id})

            # Post the account move if the journal's auto post true
            move_obj = self.env['account.move'].browse(move_id)
            if move_obj.journal_id.entry_posted:
                move_obj.post()
                move_obj.validate()

        return True

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
                        'split_method': 'by_current_cost_price',
                        'segmentation_cost': 'landed_cost'
                    }))
            if lines:
                landed_cost.update({'cost_lines': lines})
        return res

    def lcost_from_inv_line(self, inv_line):
        """Inherited from stock_landed_cost_average to set default value of
        segmentation_cost field to 'landed_cost', add default value to split
        method"""
        res = super(StockLandedCost, self). lcost_from_inv_line(inv_line)
        res.update({
            'segmentation_cost': 'landed_cost',
            'split_method': 'by_current_cost_price',
        })
        return res


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    segmentation_cost = fields.Selection(default='landed_cost')
    split_method = fields.Selection(default="by_current_cost_price")

    @api.onchange('product_id')
    @api.v7
    def onchange_product_id(self, cr, uid, ids, product_id=False,
                            context=None):
        # We first load products calling super() method.
        res = super(StockLandedCostLines, self).onchange_product_id(
            cr, uid, ids, product_id, context=context)
        res['value'].update({'split_method': 'by_current_cost_price'})
        return res


class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    picking_id = fields.Many2one('stock.picking', string='Pickings',
                                 copy=False)
