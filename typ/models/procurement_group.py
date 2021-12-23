from odoo import models
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id)
        wizard_scheduler_id = self.env.context.get("wizard_scheduler_id")
        wizard_scheduler = self.env["stock.scheduler.compute"].browse(wizard_scheduler_id)
        if wizard_scheduler.warehouse_id:
            domain = expression.AND([domain, [("warehouse_id", "=", wizard_scheduler.warehouse_id.id)]])
        if wizard_scheduler.importance:
            domain = expression.AND([domain, [("importance", "=", wizard_scheduler.importance)]])
        return domain
