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

    def search(self, cr, user, domain, offset=0, limit=None, order=None,
               context=None, count=False):
        if context is None:
            context = {}
        if context.get('order_point_domain'):
            domain.extend(context['order_point_domain'])
        return super(StockWarehouseOrderpoint, self).search(
            cr, user, domain, offset=offset, limit=limit, order=order,
            context=context, count=count)

    @api.model
    def subtract_procurements(self, orderpoint):
        """This function returns quantity of product that needs to be
        deducted from the orderpoint computed quantity because there's
        already a procurement created with aim with aim to fulfill it.
        """
        qty = super(StockWarehouseOrderpoint, self).subtract_procurements(
            orderpoint)
        for procurement in orderpoint.procurement_ids:
            if procurement.state in ('cancel', 'done'):
                continue
            for move in procurement.move_ids:
                if move.state == 'cancel':
                    # It is necesary add in total qty moves in state canceled
                    # which were deducted in SUPER function
                    qty += move.product_qty
        return qty


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

    @api.model
    def automatic_procurement_cancel(self):
        """This function is executed from a ir_cron to cancel procurements in
        exception state"""
        procurement_ids = self.search(
            [('state', '=', 'exception')])
        procurement_ids = procurement_ids.filtered(
            lambda proc: (not proc.purchase_id or
                          proc.purchase_id.state == 'cancel') and
            proc.rule_id.action == 'buy')
        # TODO When a puschase is canceled, its procurement are canceled
        # as well, that makes that relation between procurement and purchase
        # it is erased, because the purchase order line is eliminated with
        # the cancellation of the procurement
        procurement_ids.cancel()


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    @api.multi
    def unlink(self):
        if self._context.get('not_delete_purchase_line', False):
            return True
        proc_ids = self.mapped('procurement_ids')
        res = super(PurchaseOrderLine, self).unlink()
        if proc_ids:
            proc_ids.write({'state': 'cancel'})
        return res
