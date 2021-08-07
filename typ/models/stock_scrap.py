from odoo import _, models
from odoo.exceptions import UserError


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def action_validate(self):
        """Allow only warehouse managers to confirm scraps"""
        self.ensure_one()
        is_manager = self.env.user.has_group("stock.group_stock_manager")
        if not is_manager and self.location_id.usage == "internal" and self.scrap_location_id.usage == "inventory":
            group_manager = self.env.ref("stock.group_stock_manager")
            operation_error = _("You are not allowed to validate scraps.")
            group_info = _(
                "This operation is allowed for the following groups:\n%(groups_list)s",
                groups_list="\t- %s" % group_manager.display_name,
            )
            resolution_info = _("Contact your administrator to request access if necessary.")
            error_msg = "%s\n\n%s\n\n%s" % (operation_error, group_info, resolution_info)
            raise UserError(error_msg)

        return super().action_validate()
