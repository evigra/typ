# coding: utf-8

from openerp import api, models


class StockLandedCostGuides(models.Model):

    _name = 'stock.landed.cost.guide'
    _inherit = ['stock.landed.cost.guide', 'default.warehouse']

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        """If the warehouse selected is default for a Sale Team, set in
        journal_id the journal_guide_id associated to this Sale Team"""
        warehouse = self.warehouse_id.id
        res = super(StockLandedCostGuides, self).onchange_warehouse_id()
        if warehouse:
            journal_id = self.env['crm.case.section'].search([
                ('default_warehouse', '=', warehouse)]).journal_guide_id
            self.journal_id = journal_id
        return res
