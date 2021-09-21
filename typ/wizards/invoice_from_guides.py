from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class InvoiceFromGuides(models.TransientModel):
    _name = "invoice.guides"
    _description = "Invoices from Guides Wizard"

    date_invoice = fields.Date(
        "Invoice date", default=fields.Date.today(), help="Date which want to create the invoice"
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        domain=[("type", "=", "purchase")],
        help="Select the journal with which want the invoice to be created",
    )

    @api.model
    def validate_guides(self, partner, currency):
        """Validate that all guides selected have the same partner and
        currency"""
        # All guides must have the same partner, therefore len of partner must
        # be 1
        if len(partner) != 1:
            raise ValidationError(_("All guides selected must have" " the same partner"))
        # All guides must have the same currency, therefore len of currency
        # must be 1
        if len(currency) != 1:
            raise ValidationError(_("All guides selected must have" " the same currency"))

    def create_invoice(self):
        """Create invoice from the chosen guides. The invoice will have as
        partner the partner of the guides and lines as lines of the guides
        """
        ctx = self._context
        active_ids = ctx.get("active_ids", []) or []
        guides = self.env[ctx["active_model"]].browse(active_ids)
        is_invoiced = guides.filtered(lambda guide: guide.invoiced is True)
        if is_invoiced:
            msg = _("The guide(s) ")
            names = []
            for guide in is_invoiced:
                msg = msg + '"%s" '
                names.append(guide.name)
            raise ValidationError((msg + _("is already invoiced")) % tuple(names))
        partner = guides.mapped("partner_id")
        currency = guides.mapped("currency_id")
        self.validate_guides(partner, currency)
        invoice_dict = {
            "partner_id": partner.id,
            "date_invoice": self.date_invoice,
            "type": "in_invoice",
            "account_id": partner.property_account_payable_id.id,
            "currency_id": currency.id,
        }
        if self.journal_id:
            invoice_dict.update({"journal_id": self.journal_id.id})
        invoice = self.env["account.move"].create(invoice_dict)
        guides_lines = guides.mapped("line_ids")
        for line in guides_lines:
            account_line = (
                line.product_id.property_stock_account_input
                or line.product_id.categ_id.property_stock_account_input_categ_id
            )
            if not account_line:
                raise ValidationError(
                    _('Please define expense account for this product: "%s"') % (line.product_id.name)
                )
            self.env["account.move.line"].create(
                {
                    "product_id": line.product_id.id,
                    "name": line.product_id.name,
                    "account_id": account_line.id,
                    "quantity": 1.0,
                    "price_unit": line.cost,
                    "invoice_line_tax_ids": [(6, 0, [tax.id for tax in line.product_id.supplier_taxes_id])],
                    "invoice_id": invoice.id,
                    "guide_line_id": line.id,
                }
            )
        guides.write({"invoiced": True, "invoice_id": invoice.id})
        dict_return = {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_id": invoice.id,
            "views": [(False, "form")],
            "res_model": "account.move",
        }
        return dict_return