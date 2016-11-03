# -*- coding: utf-8 -*-

from openerp import fields, models, api
import openerp
from openerp.tools import float_compare, float_round
from psycopg2 import OperationalError


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
        """
        method insert warehouse_id in context & call super procure_calculation
        """
        context = dict(
            self._context,
            warehouse_id=self.warehouse_id, importance=self.importance)
        return super(ProcurementCompute,
                     self.with_context(context)).procure_calculation()


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    importance = fields.Selection([
        ('aa', 'AA'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])


class ProcurementOrder(models.Model):
    """The original path method is
        /odoo-8.0/addons/stock/procurement.py :330"""
    _inherit = "procurement.order"

    # pylint: disable=all
    @api.v7
    def _procure_orderpoint_confirm(self, cr, uid, use_new_cursor=False,
                                    company_id=False, context=None):
        '''
        Create procurement based on Orderpoint

        :param bool use_new_cursor: if set, use a dedicated cursor and
        auto-commit after processing each procurement.
            This is appropriate for batch jobs only.
        '''
        if context is None:
            context = {}
        if use_new_cursor:
            cr = openerp.registry(cr.dbname).cursor()
        orderpoint_obj = self.pool.get('stock.warehouse.orderpoint')
        procurement_obj = self.pool.get('procurement.order')
        dom = company_id and [('company_id', '=', company_id)] or []
        # Start custom patch
        if context['warehouse_id'].id:
            dom.append(('warehouse_id', '=', context['warehouse_id'].id))
        if context['importance']:
            dom.append(('importance', '=', context['importance']))
        # Stop custom patch
        orderpoint_ids = orderpoint_obj.search(cr, uid, dom)
        prev_ids = []
        while orderpoint_ids:
            ids = orderpoint_ids[:100]
            del orderpoint_ids[:100]
            for op in orderpoint_obj.browse(cr, uid, ids, context=context):
                try:
                    prods = self._product_virtual_get(cr, uid, op)
                    if prods is None:
                        continue
                    if float_compare(prods, op.product_min_qty,
                                     precision_rounding=op.product_uom.
                                     rounding) < 0:
                        qty = max(op.product_min_qty,
                                  op.product_max_qty) - prods
                        reste = (
                            op.qty_multiple > 0 and
                            qty % op.qty_multiple or 0.0)
                        if float_compare(
                            reste,
                            0.0,
                            precision_rounding=op.product_uom.rounding
                        ) > 0:
                            qty += op.qty_multiple - reste

                        if float_compare(
                            qty,
                            0.0,
                            precision_rounding=op.product_uom.rounding
                        ) <= 0:
                            continue

                        qty -= orderpoint_obj.subtract_procurements(
                            cr, uid, op, context=context)

                        qty_rounded = float_round(qty,
                                                  precision_rounding=op.
                                                  product_uom.rounding)
                        if qty_rounded > 0:
                            prepare = self._prepare_orderpoint_procurement(
                                cr, uid, op, qty_rounded, context=context)
                            proc_id = procurement_obj.create(cr, uid, prepare,
                                                             context=context)
                            self.check(cr, uid, [proc_id])
                            self.run(cr, uid, [proc_id])
                    if use_new_cursor:
                        cr.commit()
                except OperationalError:
                    if use_new_cursor:
                        orderpoint_ids.append(op.id)
                        cr.rollback()
                        continue
                    else:
                        raise
            if use_new_cursor:
                cr.commit()
            if prev_ids == ids:
                break
            else:
                prev_ids = ids

        if use_new_cursor:
            cr.commit()
            cr.close()
        return {}
