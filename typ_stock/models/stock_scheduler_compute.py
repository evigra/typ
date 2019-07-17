# -*- coding: utf-8 -*-

from openerp import fields, models


class StockSchedulerCompute(models.TransientModel):
    _inherit = 'stock.scheduler.compute'

    """Class inherit wizard Compute Stock Minimum
    """
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   help="select warehouse"
                                   " to running schedulers")

    importance = fields.Selection([
        ('aa', 'AA'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])

    def procure_calculation(self):
        """method insert warehouse_id in context & call super
        procure_calculation"""

        context = dict(
            self._context,
            warehouse_id=self.warehouse_id, importance=self.importance
        )
        return super(StockSchedulerCompute,
                     self.with_context(context)).procure_calculation()


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    def _get_orderpoint_domain(self, company_id=False):
        ctx = self._context.copy()
        if self._context.get('warehouse_id'):
            ctx.setdefault('order_point_domain', []).append(
                ('warehouse_id', '=', self._context['warehouse_id'].id)
            )
        if self._context.get('importance'):
            ctx.setdefault('order_point_domain', []).append(
                ('importance', '=', self._context['importance'])
            )
        domain = super(
            ProcurementGroup, self)._get_orderpoint_domain(company_id)
        if ctx.get('order_point_domain'):
            domain.extend(ctx['order_point_domain'])
        return domain
