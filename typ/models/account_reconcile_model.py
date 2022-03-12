from odoo import models


class AccountReconcileModel(models.Model):
    _inherit = "account.reconcile.model"

    def _get_rule_result(self, st_line, candidates, aml_ids_to_exclude, reconciled_amls_ids, partner_map):
        """Exclude candidates without access

        When displaying matched journal item candidates to reconcile, don't present the ones
        the current user doesn't have access to, to avoid access errors.
        """
        candidates = [
            candidate
            for candidate in candidates
            if self.env["account.move.line"].browse(candidate["aml_id"])._filter_access_rules_python("read")
        ]
        return super()._get_rule_result(st_line, candidates, aml_ids_to_exclude, reconciled_amls_ids, partner_map)
