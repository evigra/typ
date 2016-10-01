# -*- coding: utf-8 -*-

from openerp import models, fields, api


class StockLandedGuides (models.Model):
    _name = 'stock.landed.cost.guide'
    name = fields.Char(required=True,
                       help='Name to identify the guide')
    partner_id = fields.Many2one('res.partner',
                                 string='Partner')
    date = fields.Date()
    currency_id = fields.Many2one('res.currency',
                                  string='Currency',
                                  required=True,
                                  default=lambda self:
                                  self._get_user_default_currency())
    warehouse_id = fields.Many2one('stock.warehouse',
                                   string='Warehouse')
    line_ids = fields.One2many('stock.landed.cost.guide.line',
                               'guide_id',
                               string='Guide Lines')
    origin = fields.Char()
    destination = fields.Char()

    @api.model
    def _get_user_default_currency(self):
        """Return the default currency of the current user"""
        return self.env.user.company_id.currency_id


class StockLandedGuidesLine (models.Model):
    _name = 'stock.landed.cost.guide.line'
    guide_id = fields.Many2one('stock.landed.cost.guide')
    product_id = fields.Many2one('product.product',
                                 string='Product')
    cost = fields.Float()
    freight_type = fields.Selection([
        ('others', 'Freight - Others'),
        ('purchases', 'Freight - Purchases'),
        ('transfers', 'Freight - Transfers'),
        ('sales', 'Freight - Sales'),
        ('services', 'Services'),
    ])


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    guide_ids = fields.Many2many('stock.landed.cost.guide',
                                 'stock_landed_cost_guide_rel',
                                 'stock_landed_cost_id',
                                 'stock_landed_cost_guide_id',
                                 string='Guides',
                                 help='Guides')

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
