# -*- coding: utf-8 -*-

from openerp import fields, models

SEGMENTATION_COST = [
    ('landed_cost', 'Landed Cost'),
    ('subcontracting_cost', 'Subcontracting Cost'),
    ('material_cost', 'Material Cost'),
    ('production_cost', 'Production Cost'),
]
SEGMENTATION = ['material', 'landed', 'production', 'subcontracting']


class StockDiscrete(models.Model):

    _name = 'stock.discrete'

    cost = fields.Float()
    move_id = fields.Many2one('stock.move')
    segmentation_cost = fields.Selection(
        SEGMENTATION_COST,
        string='Segmentation',
    )


class StockMove(models.Model):

    _inherit = 'stock.move'

    discrete_ids = fields.One2many('stock.discrete', 'move_id')
