from odoo import api, fields, models


class StockSchedulerCompute(models.TransientModel):
    _inherit = "stock.scheduler.compute"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
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
        """Pass current wizard ID by context so warehouse & importance may be added to the procurement domain later

        Note:
        Not passing warehouse and importance directly because current cursor may be closed, and
        not creating a new one because Odoo will also do so in the native method [1], it's
        better to reuse the cursor created by Odoo.

        [1] https://github.com/odoo/odoo/blob/930734991ac2/addons/stock/wizard/stock_scheduler_compute.py#L25
        """
        # Environment.manage() is required because we're in a new thread where there are no envs yet,
        # so with_context() would fail without it
        with api.Environment.manage():
            self_ctx = self.with_context(wizard_scheduler_id=self.id)
        return super(StockSchedulerCompute, self_ctx)._procure_calculation_orderpoint()
