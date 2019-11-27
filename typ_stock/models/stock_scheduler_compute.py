# -*- coding: utf-8 -*-

from openerp import api, fields, models

from odoo.exceptions import UserError


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

        group_id = self.env['procurement.group'].create({})
        context = dict(
            self._context,
            warehouse_id=self.warehouse_id, importance=self.importance,
            group_id=group_id.id
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

    @api.model
    def _run_scheduler_tasks(self, use_new_cursor=False, company_id=False):
        # Minimum stock rules
        self.sudo()._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id)

        exception_moves = self.env['stock.move'].search(
            self._get_exceptions_domain())
        for move in exception_moves:
            values = move._prepare_procurement_values()
            try:
                with self._cr.savepoint():
                    origin = (move.group_id and (
                        move.group_id.name + ":") or "") + (
                            move.rule_id and move.rule_id.name or move.origin
                            or move.picking_id.name or "/")
                    self.run(
                        move.product_id, move.product_uom_qty,
                        move.product_uom, move.location_id, move.rule_id and
                        move.rule_id.name or "/", origin, values)
            except UserError as error:
                self.env['procurement.rule']._log_next_activity(
                    move.product_id, error.name)
        # pylint: disable=invalid-commit
        if use_new_cursor:
            self._cr.commit()

        # Merge duplicated quants
        self.env['stock.quant']._merge_quants()
