from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = "sale.order"

    has_order_lines = fields.Boolean(
        compute="_compute_has_order_lines",
        help="Helper field to disable partner edition in Form view",
    )

    type_payment_term = fields.Selection(
        [("credit", "Credit"), ("cash", "Cash"), ("postdated_check", "Postdated check")], default="credit"
    )
    so = fields.Boolean(
        string="Is Special Order", help="This or some product of the sales order " "will be purchased with a supplier?"
    )
    stocksale = fields.Boolean(
        string="Is Stock Sale", help="Check this box " "if it is a stock sale, if not, define " "the delivery method"
    )
    notest = fields.Text(
        string="Notes",
        help="Delivery address, product availability, "
        "special shipping instructions, "
        "conditions of purchase, etc.",
    )
    delivery_promise = fields.Date(help="Date in which we promise " "to deliver to the client")
    shipping_to = fields.Selection(
        [
            ("cliente", "CLIENTE"),
            ("t_hmo", "TIENDA HERMOSILLO"),
            ("t_cln", "TIENDA CULIACAN"),
            ("t_nog", "TIENDA NOGALES"),
            ("t_tij", "TIENDA TIJUANA"),
            ("t_cen", "TIENDA OBREGON"),
            ("t_mxl", "TIENDA MEXICALI"),
            ("t_lap", "TIENDA LA PAZ"),
            ("t_lmm", "TIENDA LOS MOCHIS"),
            ("t_gdl", "TIENDA GUADALAJARA"),
            ("aa_nog", "AGENCIA ADUANAL NOGALES"),
            ("aa_tij", "AGENCIA ADUANAL TIJUANA"),
            ("aa_mxl", "AGENCIA ADUANAL MEXICALI"),
            ("aa_nld", "AGENCIA ADUANAL NUEVO LAREDO"),
            ("aa_cjs", "AGENCIA ADUANAL CD JUAREZ"),
            ("otro", "OTRO"),
        ],
        help="Branch, customs agency or destination to which the " "merchandise will be sent from the supplier",
    )
    partial_supply = fields.Selection(
        [
            ("si", "Si"),
            ("no", "No"),
        ],
        help="Partial delivery may or may not be possible",
    )
    type_of_import = fields.Selection(
        [
            ("semanal", "Semanal"),
            ("express", "Express"),
            ("na", "N/A"),
        ],
        help="This order crosses only through customs or in a consolidated",
    )
    shipping_by = fields.Selection(
        [
            ("paquetexpress", "Paquetexpress"),
            ("consolidado", "Consolidado"),
            ("otro", "Otro"),
        ],
        help="It will be shipped by some freight company or " "in some consolidated of the provider",
    )
    purchase_currency = fields.Many2one("res.currency", help="USD / MXN")
    special_discounts = fields.Char(help="Any compensation granted by the provider")


    @api.depends("order_line")
    def _compute_has_order_lines(self):
        self.has_order_lines = bool(self.order_line)

    def write(self, vals):

        if not vals.get("partner_id"):
            return super().write(vals)

        so_partner_edited = self.filtered(
            lambda r: r.partner_id.id != vals["partner_id"]
            and r.has_order_lines
        )
        if so_partner_edited:
            raise ValidationError(
                _(
                    "You can't change Partner in Sales Orders with lines. Order IDs: %s."
                )
                % so_partner_edited.ids
            )

        return super().write(vals)

    @api.onchange("warehouse_id", "partner_id")
    def _onchange_warehouse_id(self):
        """Obtain Salesman depending on configuration warehouse in partner
        related
        """
        partner_warehouse_model = self.env["res.partner.warehouse"]
        res = super()._onchange_warehouse_id()
        res_warehouse = partner_warehouse_model.search(
            [("partner_id", "=", self.partner_id.id), ("warehouse_id", "=", self.warehouse_id.id)], limit=1
        )
        seller_id = res_warehouse.user_id
        if seller_id:
            self.user_id = seller_id
        return res

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        """Inherit to reassign origin field in procurement order"""
        res = super()._prepare_order_line_procurement(order, line, group_id)
        res.update({"origin": order.name})
        return res

    @api.onchange("type_payment_term", "partner_id")
    def get_payment_term(self):
        """Get payment term depends on type payment term."""
        self.env["account.move"].with_context({"res_id": self}).get_payment_term()

    @api.onchange("order_line")
    def check_margin(self):
        """Verify margin minimum in sale order by change in field."""
        for line in self.order_line:
            warning = line.check_margin_qty()
            if warning:
                warning["title"] = _("Sale of product below margin")
                return {
                    "warning": warning,
                }

    def action_cancel(self):
        picking_done = self.picking_ids.filtered(lambda pick: pick.state == "done")
        if picking_done:
            raise ValidationError(
                _("This order can not be canceled because " "some of their pickings already have been " "transfered.")
            )
        return super().action_cancel()

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res.update({"type_payment_term": self.type_payment_term})
        return res

    @api.onchange("order_line")
    def onchange_special_order(self):
        if self.order_line.filtered("special_sale") and not self.so:
            self.so = True  # pylint: disable=invalid-name
        if not self.order_line.filtered("special_sale") and self.so:
            self.so = False  # pylint: disable=invalid-name

    @api.onchange("partner_id")
    def onchange_partner_shipping_id(self):
        """Assignment of fiscal position, for clients with sales team in border
        location.
        """
        res = super().onchange_partner_shipping_id()
        self.fiscal_position_id = self.team_id.fiscal_position_id
        if self.partner_id.property_account_position_id and self.team_id.fiscal_position_id:
            msg = _("The partner ")
            msg = msg + _(
                "%s has a fiscal position configuration, however it "
                "is recommended to apply the border fiscal position"
            )
            warning = {
                "title": _("Warning!"),
                "message": ((msg) % self.partner_id.name),
            }
            return {"warning": warning}
        return res

    def action_invoice_create(self, grouped=False, final=False):
        """Inherited method, to add picking name in origin field to the
        dict of values to create the new invoice for a sales order.
        """
        res = super().action_invoice_create(grouped, final)
        invoice_model = self.env["account.move"]
        invoices_set = invoice_model
        invoices_new = invoice_model.browse(res)
        for sale in self:
            invoices = sale.invoice_ids & invoices_new
            pick_ids = sale.picking_ids.filtered(
                lambda pick: pick.location_dest_id.usage == "customer" and pick.state == "done"
            )
            origin_new = "%s : %s" % (sale.name, " ".join(pick_ids.mapped("name")))
            origin_old = invoices.mapped("origin") if invoices in invoices_set else []
            origin_old.append(origin_new)
            invoices.update({"origin": ", ".join(origin_old)})
            invoices_set |= invoices
        return res
