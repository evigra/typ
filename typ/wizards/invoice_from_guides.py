from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class InvoiceFromGuides(models.TransientModel):
    _name = "invoice.guides"
    _description = "Invoices from Guides Wizard"

    guide_ids = fields.Many2many(
        "stock.landed.cost.guide",
        "invoice_guide_wizard_rel",
        "wizard_id",
        "guide_id",
        string="Guides",
    )
    invoice_date = fields.Date(default=fields.Date.context_today, help="Date which want to create the invoice")
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        domain=[("type", "=", "purchase")],
        help="Select the journal with which want the invoice to be created",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get("active_ids", []) or []
        active_model = self.env.context.get("active_model", "stock.landed.cost.guide")
        guides = self.env[active_model].browse(active_ids)
        self.validate_guides(guides)
        res["guide_ids"] = [(6, 0, guides.ids)]
        return res

    @api.model
    def validate_guides(self, guides):
        """Apply some pre-validations

        Validate that all guides selected have the same partner, company and
        currency; and that are not already invoiced.
        """
        is_invoiced = guides.filtered("invoiced")
        if is_invoiced:
            raise ValidationError(
                _("The following guides are already invoiced:\n- %s", "\n- ".join(guides.mapped("display_name")))
            )

        # All guides must have the same partner, therefore len of partner must
        # be 1
        if len(guides.partner_id) != 1:
            raise ValidationError(_("All selected guides must have the same partner."))
        # All guides must have the same currency, therefore len of currency
        # must be 1
        if len(guides.currency_id) != 1:
            raise ValidationError(_("All selected guides must have the same currency."))
        if len(guides.company_id) != 1:
            raise ValidationError(_("All selected guides must have the same company."))

    def create_invoice(self):
        """Create invoice from the chosen guides. The invoice will have as
        partner the partner of the guides and lines as lines of the guides
        """
        invoice_vals = self._prepare_invoice_vals(self.guide_ids)
        invoice = self.env["account.move"].with_context(default_move_type="in_invoice").create(invoice_vals)
        self.guide_ids.write({"invoiced": True, "invoice_id": invoice.id})
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_in_invoice_type")
        action.update(
            {
                "res_id": invoice.id,
                "views": [v for v in action["views"] if v[1] == "form"],
            }
        )
        return action

    def _prepare_invoice_vals(self, guides):
        guide = guides[0]
        values = {
            "partner_id": guide.partner_id.id,
            "invoice_date": self.invoice_date,
            "move_type": "in_invoice",
            "currency_id": guide.currency_id.id,
            "company_id": guide.company_id.id,
            "invoice_line_ids": self._prepare_invoice_line_vals(guides),
        }
        if self.journal_id:
            values["journal_id"] = self.journal_id.id
        return values

    def _prepare_invoice_line_vals(self, guides):
        result = []
        for line in guides.line_ids:
            account_line = line.product_id.product_tmpl_id.get_product_accounts()["stock_input"]
            if not account_line:
                raise ValidationError(
                    _(
                        "Please configure a stock input account for the product '%s'.",
                        line.product_id.display_name,
                    )
                )
            taxes = (
                line.product_id.supplier_taxes_id
                or account_line.tax_ids
                or line.guide_id.company_id.account_purchase_tax_id
            )
            result.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "account_id": account_line.id,
                        "quantity": 1.0,
                        "price_unit": line.cost,
                        "tax_ids": [(6, 0, taxes.ids)],
                        "guide_line_id": line.id,
                    },
                )
            )

        return result
