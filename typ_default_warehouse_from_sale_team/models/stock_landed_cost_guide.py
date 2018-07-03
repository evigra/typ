# coding: utf-8

from openerp import api, fields, models


class StockLandedCostGuides(models.Model):

    _inherit = 'stock.landed.cost.guide'

    @api.multi
    def _get_landed_cost_warehouse_id(self):
        sale_team = self.env.user.sale_team_id
        return sale_team.default_warehouse.id

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        """If the warehouse selected is default for a Sale Team, set in
        journal_id the journal_guide_id associated to this Sale Team"""
        warehouse = self.warehouse_id.id
        res = {}
        if warehouse:
            journal_id = self.env['crm.team'].search([
                ('default_warehouse', '=', warehouse)]).journal_guide_id
            self.journal_id = journal_id
        return res

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=_get_landed_cost_warehouse_id,
        help='Warehouse which this guide belongs to')
