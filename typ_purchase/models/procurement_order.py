# from odoo import models


# class ProcurementRule(models.Model):

#     _inherit = "procurement.rule"

#     def _make_po_get_domain(self, values, partner):
#         """We need to create separate purchase order when is created from
#         sale order and purchase order by orderpoint should not merge with the
#         purchase order from sale order

#         to create separate purchase order just we need to set pull rule like
#         'propagate group'

#         and with this change we avoid that purchase from orderpoint merge with
#         purchase from sale order
#         """
#         res = super()._make_po_get_domain(values, partner)
#         if values.get("orderpoint_id") and not values.get("group_id"):
#             res += (("group_id", "=", False),)
#         return res
