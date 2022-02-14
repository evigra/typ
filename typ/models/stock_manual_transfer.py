from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockManualTransfer(models.Model):
    _name = "stock.manual_transfer"
    _description = "Manual Transfer"
    _inherit = ["default.warehouse.mixin", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _("New"),
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.user._get_default_warehouse_id(),
    )
    date_planned = fields.Datetime(
        "Planned Date",
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    route_id = fields.Many2one(
        "stock.location.route",
        string="Preferred Route",
        domain=[("manual_transfer_selectable", "=", True)],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    transfer_line_ids = fields.One2many(
        "stock.manual_transfer.line",
        "transfer_id",
        string="Transfer Lines",
        copy=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("valid", "Validated"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
    )
    procurement_group_id = fields.Many2one("procurement.group", copy=False)
    picking_ids = fields.One2many(
        "stock.picking",
        string="Transfers",
        compute="_compute_picking_ids",
    )

    def action_validate(self):
        procurement_group = self.env["procurement.group"].create({"name": self.name})
        values = {
            "date_planned": self.date_planned,
            "route_ids": self.route_id,
            "warehouse_id": self.warehouse_id,
            "group_id": procurement_group,
        }
        procurements = [line._create_procurement(values) for line in self.transfer_line_ids]
        self.env["procurement.group"].run(procurements)
        return self.write(
            {
                "state": "valid",
                "procurement_group_id": procurement_group.id,
            }
        )

    @api.depends("procurement_group_id")
    def _compute_picking_ids(self):
        for record in self:
            record.picking_ids = record.procurement_group_id.picking_ids

    def unlink(self):
        for record in self:
            if record.state == "valid":
                raise ValidationError(
                    _(
                        "You can not delete a validated transfer.\n- Record: %s",
                        record.name,
                    )
                )
        return super().unlink()

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(self._name)
        return super().create(vals)

    def action_view_pickings(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")
        action.update(
            {
                "domain": [("id", "in", self.picking_ids.ids)],
                "res_id": self.picking_ids[:1].id,
            }
        )
        if len(self.picking_ids) == 1:
            action["views"] = [(view_id, view_type) for view_id, view_type in action["views"] if view_type == "form"]
        return action


class StockManualTransferLine(models.Model):
    _name = "stock.manual_transfer.line"
    _description = "Manual Transfer Line"
    _order = "transfer_id, sequence, id"

    transfer_id = fields.Many2one("stock.manual_transfer", "Transfer Reference", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one(
        "product.product",
        domain=[("type", "=", "product")],
        required=True,
    )
    product_uom_qty = fields.Float("Quantity", required=True, default=1.0)
    product_uom_id = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]",
        required=True,
        compute="_compute_product_uom_id",
        store=True,
        readonly=False,
    )
    product_uom_category_id = fields.Many2one(
        "uom.category",
        string="Product's unit of measure category",
        related="product_id.uom_id.category_id",
    )

    @api.depends("product_id")
    def _compute_product_uom_id(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_id

    def _create_procurement(self, values):
        self.ensure_one()
        transfer = self.transfer_id
        return self.env["procurement.group"].Procurement(
            product_id=self.product_id,
            product_qty=self.product_uom_qty,
            product_uom=self.product_uom_id,
            location_id=transfer.warehouse_id.lot_stock_id,
            name=transfer.name,
            origin=transfer.name,
            company_id=transfer.warehouse_id.company_id,
            values=values,
        )
