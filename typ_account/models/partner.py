# -*- coding: utf-8 -*-

from openerp import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def sale_team_journals(self, warehouse, journal):
        default_sale_team = self.env['account.journal'].browse(
            journal).section_id
        if warehouse:
            default_sale_team = self.env['crm.team'].search([
                ('default_warehouse', '=', warehouse)])

        return default_sale_team.journal_team_ids.ids

    @api.multi
    def _get_credit_overloaded(self):
        for partner in self:
            context = self.env.context or {}
            currency_obj = self.env['res.currency']
            res_company = self.env['res.company']
            imd_obj = self.env['ir.model.data']
            company_id = imd_obj.get_object_reference(
                'base', 'main_company')[1]
            company = res_company.browse(company_id)
            new_amount = context.get('new_amount', 0.0)
            new_currency = context.get('new_currency', False)
            if new_currency:
                from_currency = currency_obj.browse(new_currency)
            else:
                from_currency = company.currency_id
            new_amount_currency = from_currency.compute(
                new_amount, company.currency_id)
            current_warehouse = context.get('warehouse_id', False)
            current_journal = context.get('journal_id', False)
            journals_sale_team = self.sale_team_journals(
                current_warehouse, current_journal)
            if not current_warehouse:
                # We have to search the sale team that has the journal_id in
                # journal_team_ids to obtain its default_warehouse
                default_sale_team = self.env['account.journal'].browse(
                    current_journal).section_id
                current_warehouse = default_sale_team.default_warehouse.id

            # We have to search only move line related with journals in sale
            # team with current_warehouse as default warehouse to calculate
            # partner credit
            acc_partner = self.env['res.partner']._find_accounting_partner(
                partner)
            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', acc_partner.id),
                ('account_id.internal_type', '=', 'receivable'),
                ('move_id.state', '!=', 'draft'), ('reconciled', '=', False),
                ('journal_id', 'in', journals_sale_team),
                ('debit', '!=', 0.0)])
            credit = sum(move_lines.mapped('amount_residual')) or 0.0
            warehouse_config = partner.res_warehouse_ids.filtered(
                lambda wh_conf: wh_conf.warehouse_id.id == current_warehouse)
            # If a warehouse configuration doesn't exist then it must assume
            # that credit limit in this warehouse is cero and allowed
            # only cash sales.
            if not warehouse_config:
                partner.credit_overloaded = True
            else:
                credit_limit = warehouse_config.credit_limit
                new_credit = credit + new_amount_currency
                partner.credit_overloaded = new_credit > credit_limit

    @api.multi
    def _get_overdue_credit(self):
        for partner in self:
            context = self.env.context or {}
            current_journal = context.get('journal_id', False)
            current_warehouse = context.get('warehouse_id', False)
            journals_sale_team = self.sale_team_journals(
                current_warehouse, current_journal)
            if not current_warehouse:
                # We have to search the sale team that has the journal_id in
                # journal_team_ids to obtain its default_warehouse
                default_sale_team = self.env['account.journal'].browse(
                    current_journal).section_id
                current_warehouse = default_sale_team.default_warehouse.id
            warehouse_config = partner.res_warehouse_ids.filtered(
                lambda wh_conf: wh_conf.warehouse_id.id == current_warehouse)
            acc_partner = self.env['res.partner']._find_accounting_partner(
                partner)
            movelines = self.env['account.move.line'].search([
                ('partner_id', '=', acc_partner.id),
                ('account_id.internal_type', '=', 'receivable'),
                ('move_id.state', '!=', 'draft'), ('reconciled', '=', False),
                ('journal_id', 'in', journals_sale_team)])
            debit_maturity, credit_maturity = 0.0, 0.0
            for line in movelines:
                # Allow sale if a partner has the warehouse configuration with
                # allow_overdue_invoice True
                if (not warehouse_config or not
                        warehouse_config.allow_overdue_invoice):
                    if line.date_maturity:
                        limit_day = line.date_maturity
                    else:
                        limit_day = fields.Date.today()
                    if limit_day <= fields.Date.today():
                        # credit and debit maturity sums all aml
                        # with late payments
                        debit_maturity += (line.amount_residual if
                                           line.debit else 0.0)
                    if line.credit and (line.reconcile_partial_id or
                                        line.reconcile_id):
                        credit_maturity += (line.amount_residual if
                                            line.amount_residual > 0.0 else
                                            0.0)
                    else:
                        credit_maturity += line.credit
            balance_maturity = debit_maturity - credit_maturity
            partner.overdue_credit = balance_maturity > 0.0

    @api.depends('credit_overloaded', 'overdue_credit', 'credit_limit')
    def get_allowed_sale(self):
        return super(ResPartner, self).get_allowed_sale()
