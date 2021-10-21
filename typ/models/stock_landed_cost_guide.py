from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockLandedCostGuide(models.Model):
    _name = "stock.landed.cost.guide"
    _description = "Landed Cost Guide"

    name = fields.Char(
        required=True, help="Name to identify the guide", readonly=True, states={"draft": [("readonly", False)]}
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        change_default=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company,
        help="Company which this guide belongs to",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Partner associated to this guide",
    )
    date = fields.Date(required=True, readonly=True, states={"draft": [("readonly", False)]}, help="Date of the guide")
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company.currency_id,
        help="Currency used for this guide",
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Warehouse which this guide belongs to",
    )
    amount_total = fields.Monetary(store=True, readonly=True, compute="_compute_amount")
    journal_id = fields.Many2one(
        "account.journal",
        compute="_compute_journal",
        store=True,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Journal used for this guide",
    )
    landed_cost_id = fields.Many2one(
        "stock.landed.cost", string="Landed Cost", help="Landed cost document where this guide is added", readonly=True
    )
    line_ids = fields.One2many(
        "stock.landed.cost.guide.line",
        "guide_id",
        string="Guide Lines",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Product lines associated to this guide",
    )
    reference = fields.Selection(
        selection=[
            ("prorated", "Prorated"),
            ("branch_client", "Branch Client"),
            ("charged", "Charged"),
            ("not_charged", "Not charged"),
        ],
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Reference code for this guide",
    )
    landed = fields.Boolean(
        string="Is Landed Cost validated?",
        compute="_compute_landed",
        help="This field is automatically True if the guide belongs to a" " validated Landed Cost document",
    )
    move_id = fields.Many2one(
        "account.move",
        string="Journal Entry",
        readonly=True,
        index=True,
        ondelete="restrict",
        copy=False,
        help="Link to the automatically generated Journal Items.",
    )
    account_move_name = fields.Char(
        readonly=True,
        help="Stores the name of the Journal Entry the first time the Guide is"
        " validated, so if the user cancel or reset the guide and then create"
        " it again, it will not create a new Journal Entry Sequence, it will"
        " use always the same",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("valid", "Valid"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        default="draft",
        help="Guide status",
    )
    comments = fields.Text(
        help="Reference to track guide, folio invoice, folio sales order," " authorized customer, refill, etc."
    )
    invoiced = fields.Boolean(
        readonly=True,
        help="When the guide has been invoiced, this field is True, otherwise False",
    )
    invoice_id = fields.Many2one(
        "account.move", string="Invoice", help="Refers the invoice related whit" " this guide"
    )
    carrier_invoice = fields.Char(help="Field to add the carrier invoice number")

    @api.depends("line_ids.cost")
    def _compute_amount(self):
        for guide in self:
            guide.amount_total = sum(guide.line_ids.mapped("cost"))

    @api.depends("warehouse_id")
    def _compute_journal(self):
        for guide in self:
            guide.journal_id = guide.warehouse_id.sale_team_ids.filtered("journal_guide_id")[:1].journal_guide_id

    def _compute_landed(self):
        """Set 'landed' field to True if the Landed Cost document of this guide
        is in Valid state"""
        for guide in self:
            lc = guide.landed_cost_id
            guide.landed = lc and lc.state == "done"

    def unlink(self):
        details = ""
        for guide in self:
            if guide.account_move_name:
                details += _("Guide '%s' cannot be removed when it is/was validated\n") % (guide.name)
        if details:
            msg = _(
                "You are trying to delete guides you can not delete:\n\n%s\n"
                "Please solve this errors before continuing.",
                details,
            )
            raise ValidationError(msg)
        return super().unlink()

    def action_cancel(self):
        """Move the guide to Cancelled state, it's used when the Guide is
        associated to a Landed Cost Document because in this condition the
        guide can not be removed"""
        for guide in self:
            self._cancel_moves()
            guide.state = "cancel"

    def action_draft(self):
        for guide in self:
            if guide.landed_cost_id:
                raise ValidationError(
                    _(
                        "You cannot reset this guide to draft while it is"
                        " associated to a Landed Cost Document:\n\n- %s",
                        guide.landed_cost_id.name,
                    )
                )
            self._cancel_moves()
            guide.state = "draft"

    def _cancel_moves(self):
        if not self.move_id:
            return True
        moves = self.move_id
        # First, detach the move ids
        self.write({"move_id": False})
        # second, invalidate the move(s)
        moves.button_draft()
        # delete the move this guide was pointing to
        # Note that the corresponding move_lines and move_reconciles
        # will be automatically deleted too
        moves.with_context(force_delete=True).unlink()
        return True

    def action_valid(self):
        self.action_move_create()
        self.state = "valid"

    def action_move_create(self):
        """Creates guide related financial move lines"""
        account_move = self.env["account.move"]
        for guide in self:
            guide = guide.with_context(lang=guide.partner_id.lang or guide.company_id.partner_id.lang)
            if not guide.line_ids:
                raise UserError(
                    _(
                        "There are no Guide Lines!\n\n"
                        "Please create some guide lines before validating this document."
                    )
                )
            if guide.move_id:
                continue
            journal = guide.journal_id
            ref = guide.reference or guide.name
            company_currency = guide.company_id.currency_id
            gml = self.env["stock.landed.cost.guide.line"].move_line_get(self.id)

            gml = guide.compute_guide_totals(company_currency, ref, gml)[2]

            part = self.env["res.partner"]._find_accounting_partner(guide.partner_id)

            line = [(0, 0, self.line_get_convert(li, part.id, guide.date)) for li in gml]
            line = guide.finalize_guide_move_lines(line)
            move_vals = {
                "ref": ref,
                "line_ids": line,
                "journal_id": journal.id,
                "date": guide.date,
                "company_id": guide.company_id.id,
            }
            if guide.account_move_name:
                move_vals["name"] = guide.account_move_name

            move = account_move.with_context(lang=self.env.user.lang).create(move_vals)

            # make the guide point to that move
            guide.write({"move_id": move.id})
            # Pass guide in context in method post: used if you want to get
            # the same
            # account move reference when creating the same guide after a
            # cancelled one:
            move.action_post()
            guide.account_move_name = move.name
        return True

    def compute_guide_totals(self, company_currency, ref, guide_move_lines):
        total = 0
        total_currency = 0
        currency = self.currency_id.with_context(date=self.date or fields.Date.context_today(self))
        for line in guide_move_lines:
            line["ref"] = ref
            line["currency_id"] = False
            line["amount_currency"] = False
            if self.currency_id != company_currency:
                line["currency_id"] = currency.id
                line["amount_currency"] = currency.round(line["price"])
                line["price"] = currency.compute(line["price"], company_currency)
        return total, total_currency, guide_move_lines

    @api.model
    def line_get_convert(self, line, part, date):
        return {
            "date_maturity": line.get("date_maturity", False),
            "partner_id": part,
            "name": line["name"][:64],
            "date": date,
            "debit": line["price"] > 0 and line["price"],
            "credit": line["price"] < 0 and -line["price"],
            "account_id": line["account_id"],
            "amount_currency": line["price"] > 0
            and abs(line.get("amount_currency", False))
            or -abs(line.get("amount_currency", False)),
            "currency_id": line.get("currency_id", False),
            "ref": line.get("ref", False),
            "quantity": line.get("quantity", 1.00),
            "product_id": line.get("product_id", False),
            "product_uom_id": line.get("uos_id", False),
            "analytic_account_id": line.get("account_analytic_id", False),
            "guide_line_id": line.get("guide_line_id", False),
        }

    def finalize_guide_move_lines(self, move_lines):
        """finalize_guide_move_lines(move_lines) -> move_lines

        Hook method to be overridden in additional modules to verify and
        possibly alter the move lines to be created by a guide, for
        special cases.
        :param move_lines: list of dictionaries with the account.move.lines
        (as for create())
        :return: the (possibly updated) final move_lines to create for this
        guide
        """
        return move_lines

    def view_accrual(self):
        """Launches a view with the account.move.lines related to the current guide"""
        action = self.env.ref("account.action_move_line_select").read()[0]
        action.update(
            {
                "domain": [("guide_line_id", "in", self.line_ids.ids)],
                "context": {},
            }
        )
        return action


class StockLandedGuidesLine(models.Model):
    _name = "stock.landed.cost.guide.line"
    _description = "Landed Cost Guide Line"

    guide_id = fields.Many2one("stock.landed.cost.guide", help="Guide which this line belongs to")
    product_id = fields.Many2one(
        "product.product",
        domain="[('landed_cost_ok', '=', True)]",
        help="Product associated to this line",
    )
    cost = fields.Float(help="Cost of the operation on this line")
    freight_type = fields.Selection(
        selection=[
            ("transfers", "Restocked"),
            ("purchases", "Purchases"),
            ("sales", "Firm Sale"),
            ("salesc", "Branch-Client Sale"),
            ("others", "Others"),
            ("services", "Services"),
        ],
        help="Freight type of this operation",
    )

    @api.model
    def product_stock_account_in(self):
        """Returns the ID for the 'stock_account_input' of the current line
        product"""
        product_tmpl = self.product_id.product_tmpl_id
        accounts = product_tmpl.get_product_accounts()
        return accounts["stock_input"]

    @api.model
    def move_line_get(self, guide_id):
        guide_brw = self.env["stock.landed.cost.guide"].browse(guide_id)
        res = []
        for line in guide_brw.line_ids:

            debit = self.move_line_get_item(line)
            res.append(debit)

            # Reverse entry line for the input account
            credit = debit.copy()
            credit.update(
                {
                    "account_id": line.product_stock_account_in().id,
                    "price": credit["price"] * -1,
                    "guide_line_id": line.id,
                }
            )
            res.append(credit)
        return res

    @api.model
    def move_line_get_item(self, line):
        account = line.product_id.categ_id.property_account_expense_categ_id
        return {
            "type": "src",
            "name": line.product_id.name.split("\n")[0][:64],
            "price_unit": line.cost,
            "account_id": account.id,
            "price": line.cost,
            "product_id": line.product_id.id,
        }
