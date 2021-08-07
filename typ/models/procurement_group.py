from odoo import models
from odoo.osv import expression


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    def _get_orderpoint_domain(self, company_id=False):
        domain = super()._get_orderpoint_domain(company_id)
        warehouse_id = self.env.context.get("scheduler_warehouse_id")
        if warehouse_id:
            domain = expression.AND(domain, [("warehouse_id", "=", warehouse_id)])
        importance = self.env.context.get("scheduler_importance")
        if importance:
            domain = expression.AND(domain, [("importance", "=", importance)])
        return domain
