from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Make selectable only pricelists matching the SO's partner
    pricelist_id = fields.Many2one(
        domain="""[
            ('partner_ids', '=', partner_id),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', company_id),
        ]""",
    )
    # Order date always readonly
    date_order = fields.Datetime(states=None)
    type_payment_term = fields.Selection(
        selection=[
            ("credit", "Credit"),
            ("cash", "Cash"),
            ("postdated_check", "Postdated check"),
        ],
        default="credit",
    )
    is_special = fields.Boolean(
        string="Is Special Order",
        help="This or some product of the sales order will be purchased with a vendor?",
    )
    stocksale = fields.Boolean(
        string="Is Stock Sale",
        help="Check this box if it is a stock sale, if not, define the delivery method",
    )
    notest = fields.Text(
        string="Notes",
        help="Delivery address, product availability, "
        "special shipping instructions, "
        "conditions of purchase, etc.",
    )
    delivery_promise = fields.Date(help="Date in which we promise " "to deliver to the client")
    shipping_to = fields.Selection(
        selection=[
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
        help="Branch, customs agency or destination to which the merchandise will be sent from the supplier",
    )
    partial_supply = fields.Selection(
        selection=[
            ("si", "Si"),
            ("no", "No"),
        ],
        help="Partial delivery may or may not be possible",
    )
    type_of_import = fields.Selection(
        selection=[
            ("semanal", "Semanal"),
            ("express", "Express"),
            ("na", "N/A"),
        ],
        help="This order crosses only through customs or in a consolidated",
    )
    shipping_by = fields.Selection(
        selection=[
            ("paquetexpress", "Paquetexpress"),
            ("consolidado", "Consolidado"),
            ("otro", "Otro"),
        ],
        help="It will be shipped by some freight company or in some consolidated of the provider",
    )
    purchase_currency = fields.Many2one("res.currency", help="USD / MXN")
    special_discounts = fields.Char(help="Any compensation granted by the provider")

    def write(self, vals):
        if "partner_id" not in vals:
            return super().write(vals)

        so_partner_edited = self.filtered(lambda so: so.partner_id.id != vals["partner_id"] and so.order_line)
        if so_partner_edited:
            raise ValidationError(
                _(
                    "You can't change Partner in Sales Orders with lines. Order IDs: %s.",
                    so_partner_edited.ids,
                )
            )

        return super().write(vals)

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        """Inherit to reassign origin field in procurement order"""
        res = super()._prepare_order_line_procurement(order, line, group_id)
        res.update({"origin": order.name})
        return res

    @api.onchange("order_line")
    def _onchange_order_line(self):
        """Verify margin minimum in sale order by change in field."""
        for line in self.order_line:
            warning = line.check_margin_qty()
            if warning:
                warning["title"] = _("Sale of product below margin")
                return {
                    "warning": warning,
                }

        self.is_special = bool(self.order_line.filtered("special_sale"))

    @api.onchange("partner_id")
    def _onchange_partner_shipping_id(self):
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
