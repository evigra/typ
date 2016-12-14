# -*- coding: utf-8 -*-

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    exchange_landed_ids = fields.Many2many(
        'stock.landed.cost',
        'landed_invoice_rel',
        'invoice_id', 'landed_id',
        string='Exchange Differential Landed',
        help='Landed created to adjust '
        'the cost of the product by '
        'exchange differential')

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        res['guide_line_id'] = line.get('guide_line_id', False)
        return res

    @api.multi
    def invoice_validate(self):
        """Overwritten to create a new landed to update the valuation of the
        products using the rate according to the date invoice.
        If the partner is foreign the date used will be a day before invoice
        data at the moment to validate it
        """
        res = super(AccountInvoice, self).invoice_validate()
        landed = self.env['stock.landed.cost']
        adjust_method = landed.adjust_cost_for_exchange_differential
        for inv in self:
            if (inv.currency_id != inv.company_id.currency_id and
                    inv.partner_id.country_id == inv.company_id.country_id and
                    inv.type == 'in_invoice'):
                landed = adjust_method(inv, inv.date_invoice)
                inv.exchange_landed_ids = landed
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    guide_line_id = fields.Many2one(
        'stock.landed.cost.guide.line', help='Guide line associated to this'
        ' invoice')

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        res['guide_line_id'] = line.guide_line_id.id
        return res
