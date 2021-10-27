from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockManualTransfer(models.Model):
    _name = "stock.manual_transfer"
    _description = "TODO: Once talk with the team describe it for v14.0"
    _inherit = ["mail.thread"]

    name = fields.Char(copy=False, readonly=True)
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        "Warehouse",
        required=True,
        default=lambda self: self.env.user.sale_team_id.default_warehouse.id,
    )
    date_planned = fields.Datetime("Planned Date", default=fields.Datetime.now, required=True)
    route_id = fields.Many2one(
        "stock.location.route", "Preferred Routes", domain=[("manual_transfer_selectable", "=", True)], required=True
    )
    transfer_line = fields.One2many("stock.manual_transfer_line", "transfer_id", string="Transfer Lines", copy=True)
    state = fields.Selection([("draft", "Draft"), ("valid", "Valid")], default="draft", tracking=True)
    procurement_group_id = fields.Many2one("procurement.group", "Procurement Group", copy=False)
    picking_ids = fields.One2many("stock.picking", compute="_compute_picking_ids")

    def make_transfer(self):
        group_id = self.env["procurement.group"].create({"name": self.name})
        values = {
            "date_planned": self.date_planned,
            "route_ids": self.route_id,
            "warehouse_id": self.warehouse_id,
            "group_id": group_id,
        }

        for move in self.transfer_line:
            self.env["procurement.group"].run(
                move.product_id,
                move.product_uom_qty,
                move.product_uom,
                self.warehouse_id.lot_stock_id,
                "/",
                self.name,
                values,
            )
        self.state = "valid"
        self.procurement_group_id = group_id

    @api.depends("procurement_group_id")
    def _compute_picking_ids(self):
        for record in self.filtered("procurement_group_id"):
            record.picking_ids = record.env["stock.picking"].search(
                [("group_id", "=", record.procurement_group_id.id)]
            )

    def unlink(self):
        for record in self.filtered(lambda r: r.state == "valid"):
            raise ValidationError(_("You can not delete a valid transaction! (%s)") % record.name)
        return super().unlink()

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("manual.transfers")
        return super().create(vals)

    def action_view_pickings(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action.update(
            {
                "domain": [("id", "in", self.picking_ids.ids)],
                "res_id": self.picking_ids[:1].id,
            }
        )
        if len(self) != 1:
            action["views"] = [(view_id, view_type) for view_id, view_type in action["views"] if view_type == "form"]
        return action


class StockManualTransferLine(models.Model):
    _name = "stock.manual_transfer_line"
    _description = "Manual Transfer Line"

    transfer_id = fields.Many2one("stock.manual_transfer", "Transfer Reference", ondelete="cascade")
    product_id = fields.Many2one(
        "product.product", domain=[("type", "=", "product")], ondelete="restrict", required=True
    )
    product_uom_qty = fields.Float("Quantity", required=True, default=1.0)
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure", required=True)

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_uom = self.product_id.uom_id
        return {"domain": {"product_uom": [("category_id", "=", self.product_id.uom_id.category_id.id)]}}
