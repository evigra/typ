from odoo import fields, models


class StockSchedulerCompute(models.TransientModel):
    _inherit = "stock.scheduler.compute"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        help="select warehouse to running schedulers",
    )
    importance = fields.Selection(
        selection=[
            ("aa", "AA"),
            ("a", "A"),
            ("b", "B"),
            ("c", "C"),
            ("d", "D"),
        ]
    )

    def _procure_calculation_orderpoint(self):
        """Pass warehouse and importance by context so they are added to the procurement domain later"""
        group = self.env["procurement.group"].create({})
        context = {
            "scheduler_warehouse_id": self.warehouse_id.id,
            "scheduler_importance": self.importance,
        }
        if self.warehouse_id or self.importance:
            group = self.env["procurement.group"].create({})
            context["scheduler_group_id"] = group.id
        return super(StockSchedulerCompute, self.with_context(**context)).procure_calculation()
