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


# class StockCardProduct(models.TransientModel):
#     _inherit = 'stock.card.product'

#     def _get_discrete_values(self, move_id):
#         query = ('''
#                  SELECT
#                     cost, segmentation_cost
#                  FROM stock_discrete AS sd
#                  WHERE sd.move_id = %(move_id)s
#                  ''') % dict(move_id=move_id)
#         self._cr.execute(query)
#         return self._cr.dictfetchall()

#     def _get_price_on_customer_return(self, row, vals, qntval):
#         vals['product_qty'] += (vals['direction'] * row['product_qty'])
#         dqnt_val = self._get_discrete_values(row['move_id'])
#         # NOTE: Identify the originating move_id of returning move
#         origin_id = row['origin_returned_move_id'] or row['move_dest_id']
#         # NOTE: Falling back to average in case customer return is
#         # orphan, i.e., return was created from scratch
#         old_average = (
#             vals['move_dict'].get(origin_id) and
#             vals['move_dict'][origin_id]['average'] or vals['average'])
#         # /!\ NOTE: Normalize this computation
#         vals['move_valuation'] = sum(
#             [old_average * qnt['qty'] for qnt in qntval] +
#             [dquant['cost'] * row['product_qty']
#              for dquant in dqnt_val])

#         for sgmnt in SEGMENTATION:
#             old_average = (
#                 vals.get('global_val') and
#                 vals['global_val'].get(origin_id) and
#                 vals['global_val'][origin_id][sgmnt] or
#                 vals['move_dict'].get(origin_id) and
#                 vals['move_dict'][origin_id][sgmnt] or
#                 vals[sgmnt])

#             vals['%s_valuation' % sgmnt] = sum(
#                 [old_average * qnt['qty'] for qnt in qntval] +
#                 [dquant['cost'] * row['product_qty']
#                  for dquant in dqnt_val
#                  if dquant['segmentation_cost'] == '%s_cost' % sgmnt])
#         return True
