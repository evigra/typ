# -*- coding: utf-8 -*-

from openerp import fields, models, api


class ProcurementCompute(models.TransientModel):
    """Class inherit wizard Compute Stock Minimum
    """

    _inherit = "procurement.orderpoint.compute"

    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
                                   help="select warehouse"
                                   " to running schedulers")

    importance = fields.Selection([
        ('aa', 'AA'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])

    @api.multi
    def procure_calculation(self):
        """method insert warehouse_id in context & call super
        procure_calculation"""

        context = dict(
            self._context,
            warehouse_id=self.warehouse_id, importance=self.importance)
        return super(ProcurementCompute,
                     self.with_context(context)).procure_calculation()


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    importance = fields.Selection([
        ('aa', 'AA'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])

    @api.model
    def search(self, domain):
        ctx = self._context
        if ctx.get('order_point_domain'):
            domain.extend(self._context['order_point_domain'])
        return super(StockWarehouseOrderpoint, self).search(domain)


class ProcurementOrder(models.Model):
    """Executes the procurement orders and assigns selected values for the
    same ones
    """

    _inherit = "procurement.order"

    @api.model
    def _search_suitable_rule(self, procurement, domain):
        """This method it is overwrite in order to allow propagate pule rule
        from warehouse to another when the user has not access.
        e.g. The user A have access only into warehouse A but when create
        one sale order with route that make purchase order to warehouse B and
        resupply the warehouse A we need to propagate procurement to
        warehouse B with procurement.sudo()"""

        return super(ProcurementOrder, self)._search_suitable_rule(
            procurement.sudo(), domain)

    @api.v7
    def _procure_orderpoint_confirm(self, cr, uid, use_new_cursor=False,
                                    company_id=False, context=None):

        ctx = context.copy()
        if context.get('warehouse_id'):
            ctx.setdefault('order_point_domain', []).append(
                ('warehouse_id', '=', context['warehouse_id'].id))
        if context.get('importance'):
            ctx.setdefault('order_point_domain', []).append(
                ('importance', '=', context['importance']))
        return super(ProcurementOrder, self)._procure_orderpoint_confirm(
            cr, uid, use_new_cursor, company_id, context=ctx)
