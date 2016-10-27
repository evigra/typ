# -*- coding: utf-8 -*-

from openerp import models, api


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    # pylint: disable=W0622
    def _domain_move_lines_for_reconciliation(
            self, st_line, excluded_ids=None, str=False,
            additional_domain=None):

        if additional_domain is None:
            additional_domain = []

        additional_domain.append(
            ('account_id.type', 'in', ('payable', 'receivable')))
        return super(AccountBankStatementLine,
                     self)._domain_move_lines_for_reconciliation(
                         st_line, excluded_ids, str, additional_domain)

    @api.model
    def create_move_line_tax_payment(
            self, mv_line_dicts, partner_id, period_id, journal_id, date_st,
            type_payment, parent, company_currency, statement_currency,
            move_id=None, statement_currency_line=None):
        """This Method overwritten to create advances to employees by the model
        bank statement without generating a line for tax, associated with the
        percentage of purchases of the company
        :param @mv_line_dicts: dict with data of line to statement
        :param @partner_id: partner associated to statement
        :param @period_id: period associated to statement
        :param @journal_id: journal associated to statement
        :param @date_st: date string associated to statement
        :param @type_payment: id of currency of the payment
        :param @parent: browse record of the voucher.line
            and bank.statement.line for which we want to create currency rate
            difference accounting entries
        :param @company_currency: id of currency of the company to which
            the payment belong
        :param @statement_currency: id of currency of the payment
        :param @move_id: id of policy
        :param @statement_currency_line: id of currency of the payment
        :return: the account move line and its counterpart to create,
            depicted as mapping between fieldname and value
        :rtype: list of dict
        """

        employee = self.env['hr.employee'].search([
            ('address_home_id', '=', partner_id)])

        mv_line_dicts = not employee and mv_line_dicts or []

        return super(AccountBankStatementLine,
                     self).create_move_line_tax_payment(
                         mv_line_dicts, partner_id, period_id, journal_id,
                         date_st, type_payment, parent, company_currency,
                         statement_currency, move_id, statement_currency_line)
