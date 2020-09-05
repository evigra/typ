
from openerp import fields
from openerp.tests import common


class TestTypAccount(common.TransactionCase):

    def setUp(self):
        super(TestTypAccount, self).setUp()
        self.account_invoice = self.env['account.invoice']
        self.sale_order_model = self.env['sale.order']
        self.product = self.env.ref('product.product_product_6')
        self.partner = self.env.ref('typ_sale.partner_01')
        self.warehouse = self.env.ref('typ_sale.wh_01')
        self.warehouse_2 = self.env.ref('typ_stock.whr_test_01')
        self.journal = self.journalrec = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1)
        self.journal_bank = self.env['account.journal'].create(
            {'name': 'Bank', 'type': 'bank', 'code': 'BNK67'})
        self.sale_team = self.env['crm.team'].create({
            'name': 'Sale team 01',
            'default_warehouse': self.warehouse.id,
            'journal_team_ids': [
                (6, 0, [self.journal_bank.id, self.journal.id])]
        })
        self.account = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_receivable').id)], limit=1)
        self.account_line_product = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref(
                'account.data_account_type_revenue').id)], limit=1)
        self.payment_term_credit = self.env.ref(
            'payment_term_type.payment_term_credit')
        self.payment_term_cash = self.env.ref(
            'account.account_payment_term_immediate')
        self.conf_warehouse = self.env.ref('typ_sale.res_partner_wh_01')
        self.acc_bank_stmt_model = self.env['account.bank.statement']
        self.acc_bank_stmt_line_model = self.env['account.bank.statement.line']
        self.pricelist = self.env.ref('product.list0')
        self.account_invoice_1 = self.create_invoice()
        self.account_invoice_2 = self.create_invoice()
        self.pricelist.currency_id = self.env.user.company_id.currency_id.id

        self.dict_vals_sale = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'payment_term_id': self.payment_term_credit.id,
            'warehouse_id': self.warehouse.id,
            'pricelist_id': self.pricelist.id,
            'order_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
                  'price_unit': 900, })], }
        self.sale_order = self.sale_order_model.create(
            self.dict_vals_sale.copy())

    def create_invoice(self):
        self.dict_vals = {
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'payment_term_id': self.payment_term_credit.id,
            'journal_id': self.journal.id,
            'name': 'out_invoice',
            'invoice_line_ids': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'quantity': 1, 'price_unit': 900,
                  'account_id': self.account_line_product.id})], }
        return self.account_invoice.create(self.dict_vals.copy())

    def create_statement(self, partner, amount, journal=None,
                         line_invoice=None, date_bank=None, account_id=None,
                         currency=None, amount_currency=0):

        bank_stmt_id = self.acc_bank_stmt_model.create({
            'journal_id': journal and journal.id or self.journal_bank.id,
            'date': date_bank or fields.Date.today(),
        })

        bank_stmt_line_id = self.acc_bank_stmt_line_model.create({
            'name': 'payment',
            'statement_id': bank_stmt_id.id,
            'partner_id': partner.id,
            'amount': amount,
            'currency_id': currency,
            'amount_currency': amount_currency,
            'date': date_bank or fields.Date.today(), })

        amount = amount_currency and amount_currency or amount

        val = {
            'credit': amount > 0 and amount or 0,
            'debit': amount < 0 and amount * -1 or 0,
            'name': line_invoice and line_invoice.name or 'Advance Employee'}

        if line_invoice:
            val.update({'counterpart_move_line_id': line_invoice.id})

        if account_id:
            val.update({'account_id': account_id.id})

        bank_stmt_line_id.process_reconciliation([val])
        move_line_ids_complete = bank_stmt_id.move_line_ids
        return move_line_ids_complete
