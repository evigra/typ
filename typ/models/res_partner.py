import collections
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    map_location = fields.Text(help="Embeded url from google maps")
    facebook_profile = fields.Char(help="URL for the Facebook profile")
    linkedin_profile = fields.Char()
    upgradable = fields.Boolean("Category Can be Improved",
                                help="Mark this box if you want to allow the customer to upgradeits category.")
    importance = fields.Selection([
        ('AA', 'AA'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('X', 'X'),
        ('NEW', 'NEW'),
        ('NEGOTIATION', 'NEGOTIATION'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED')
    ])
    potential_importance = fields.Selection([
        ('AA', 'AA'),
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('X', 'X'),
        ('NEW', 'NEW'),
        ('NEGOTIATION', 'NEGOTIATION'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED')
    ])
    business_activity = fields.Selection([
        ('CONTRACTORS', 'CON'),
        ('COMPANY', 'COM'),
        ('WHOLESALERS', 'WHO'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('PUBLIC', 'PUBLIC')
    ], help="Not classified \nCON - Contractor\nCOM - Company\nWHO - Wholesaler")
    partner_type = fields.Selection([
        ('OC', 'OC - Operator contractor'),
        ('NC', 'NC - New work contractor'),
        ('PC', 'PC - Professional contractor'),
        ('RC', 'RC - Refrigeration contractor'),
        ('ESP', 'ESP - Specifier'),
        ('FSC', 'FSC - Foodstuff company'),
        ('SUP', 'SUP - Supermarket company'),
        ('BOT', 'BOT - Bottler'),
        ('OTH', 'OTH - Others'),
        ('WHC', 'WHC - Wholesaler contractor'),
        ('WW', 'WW - Wholesaler wholesaler'),
        ('WI', 'WI - Wholesaler ironmonger'),
        ('DH', 'DH - HVACR distributors'),
        ('NOT CLASSIFIED', 'NOT CLASSIFIED'),
        ('EMPLOYEE', 'EMPLOYEE'),
        ('PUBLIC', 'PUBLIC')
    ])
    dealer = fields.Selection([
        ('PD', 'PD - Premier dealer'),
        ('AD', 'AD - Authorized dealer'),
        ('SD', 'SD - Sporadic dealer')
    ], 'Dealer type')
    region = fields.Selection([
        ('NORTHWEST', 'NORTHWEST'),
        ('WEST', 'WEST'),
        ('CENTER', 'CENTER'),
        ('NORTHEAST', 'NORTHEAST'),
        ('SOUTHEAST', 'SOUTHEAST'),
        ('SOUTH', 'SOUTH')
    ])
    res_warehouse_ids = fields.One2many(
        comodel_name='res.partner.warehouse', inverse_name='partner_id', string='Warehouse configuration',
        help='Configurate salesman and credit limit to each warehouse')

    @api.constrains('res_warehouse_ids')
    def unique_conf_partner_warehouse(self):
        for res in self:
            warehouse_ids = [res_wh.warehouse_id for res_wh in res.res_warehouse_ids]
            dict_values = dict(collections.Counter(warehouse_ids))
            for key in dict_values.keys():
                if dict_values[key] > 1:
                    raise ValidationError(_('There is more than one configuration for warehouse %s. It must have only '                                            'one configuration'
                                            ' for each warehouse') % (key.name))

    @api.model
    def _merge_partner(self, form_data):
        """Verify that a partner has the necessary validations to be upgraded to a new category.
        To do this, check that the mail does not belong to another user and that it is upgradeable.
        Once validated, the user information is updated with the data entered in the form.
        """
        raise UserWarning("Not implementeed for typ in 14.0 yet")
        email = form_data.get("email")
        p_found = self.search(
            [("email", "=", email), ("upgradable", "=", True)], limit=1
        )
        duplicate_partner = self.env["res.users"].search(
            [("login", "=", email), ("partner_id", "!=", p_found.id)]
        )
        if duplicate_partner:
            return {
                "error_title": _("This email already has upgraded " "or have portal access"),
                "error": _("please contact us if you think this is a mistake"),
            }
        if not p_found:
            return {
                "error_title": _("You are not elegible for upgrade"),
                "error": _("please contact us if you think this is a mistake"),
            }
        pw = self.env["portal.wizard"]
        cpw = self.env["change.password.wizard"]
        categs = {
            "titanium": "AA",
            "black": "A",
        }
        # update values in the partner record
        category = form_data.get("category")
        values = {
            "name": form_data.get("name"),
            "street_name": form_data.get("street_name"),
            "street_number": form_data.get("street_number"),
            "street_number2": form_data.get("street_number2"),
            "zip": form_data.get("zip"),
            "street2": form_data.get("l10n_mx_edi_colony"),
            "l10n_mx_edi_colony": form_data.get("l10n_mx_edi_colony"),
            "facebook_profile": form_data.get("facebook_profile"),
            "linkedin_profile": form_data.get("linkedin_profile"),
            "upgradable": False,
            "importance": categs.get(category, False),
        }
        p_found.write(values)
        # give portal access
        portal_wizard = pw.create(
            {
                "portal_id": self.env["res.groups"]
                .search([("is_portal", "=", True)], limit=1)
                .id,
                "user_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": p_found.id,
                            "email": p_found.email,
                            "in_portal": True,
                        },
                    )
                ],
            }
        )
        portal_wizard.action_apply()
        user_id = self.env["res.users"].search(
            [("partner_id", "=", p_found.id)]
        )
        # set new password to freshly created res.user
        reset_pwd_wizard = cpw.create(
            {
                "user_ids": [
                    (
                        0,
                        0,
                        {
                            "user_id": user_id.id,
                            "user_login": user_id.email,
                            "new_passwd": form_data.get("password"),
                        },
                    )
                ],
            }
        )
        reset_pwd_wizard.change_password_button()
        return {"partner": p_found, "category": category}

    @api.model
    def _get_partner_shippings(self):
        self.ensure_one()
        shippings = self.search(
            [
                ("id", "child_of", self.commercial_partner_id.ids),
                "|",
                ("type", "=", "delivery"),
                ("id", "=", self.commercial_partner_id.id),
            ],
            order="id desc",
        )
        return shippings

    @api.model
    def _get_my_quotations(self, limit=6):
        self.ensure_one()
        sale_order = self.env["sale.order"]
        domain = [
            ("message_partner_ids", "child_of", [self.commercial_partner_id.id]),
            ("state", "in", ["sent", "cancel"]),
        ]
        return sale_order.search(domain, limit=limit)

    @api.model
    def _get_my_orders(self, limit=None):
        self.ensure_one()
        sale_order = self.env["sale.order"]
        domain = [
            (
                "message_partner_ids",
                "child_of",
                [self.commercial_partner_id.id],
            ),
            ("state", "in", ["sale", "done"]),
        ]
        return sale_order.search(domain, limit=limit)

    @api.model
    def _get_my_invoices(self, limit=None):
        self.ensure_one()
        acc_invoice = self.env["account.move"]
        domain = [
            ("type", "in", ["out_invoice", "out_refund"]),
            (
                "message_partner_ids",
                "child_of",
                [self.commercial_partner_id.id],
            ),
            ("state", "in", ["open", "paid", "cancel"]),
        ]
        return acc_invoice.search(domain, limit=limit)
    def sale_team_journals(self, warehouse, journal):
        default_sale_team = self.env["account.journal"].browse(journal).section_id
        if warehouse:
            default_sale_team = self.env["crm.team"].search([("default_warehouse", "=", warehouse)])

        return default_sale_team.journal_team_ids.ids

    def _get_credit_overloaded(self):
        for partner in self:
            context = self.env.context or {}
            currency_obj = self.env["res.currency"]
            res_company = self.env["res.company"]
            imd_obj = self.env["ir.model.data"]
            company_id = imd_obj.get_object_reference("base", "main_company")[1]
            company = res_company.browse(company_id)
            new_amount = context.get("new_amount", 0.0)
            new_currency = context.get("new_currency", False)
            if new_currency:
                from_currency = currency_obj.browse(new_currency)
            else:
                from_currency = company.currency_id
            new_amount_currency = from_currency.compute(new_amount, company.currency_id)
            current_warehouse = context.get("warehouse_id", False)
            current_journal = context.get("journal_id", False)
            journals_sale_team = self.sale_team_journals(current_warehouse, current_journal)
            if not current_warehouse:
                # We have to search the sale team that has the journal_id in
                # journal_team_ids to obtain its default_warehouse
                default_sale_team = self.env["account.journal"].browse(current_journal).section_id
                current_warehouse = default_sale_team.default_warehouse.id

            # We have to search only move line related with journals in sale
            # team with current_warehouse as default warehouse to calculate
            # partner credit
            acc_partner = self.env["res.partner"]._find_accounting_partner(partner)
            move_lines = self.env["account.move.line"].search(
                [
                    ("partner_id", "=", acc_partner.id),
                    ("account_id.internal_type", "=", "receivable"),
                    ("move_id.state", "!=", "draft"),
                    ("reconciled", "=", False),
                    ("journal_id", "in", journals_sale_team),
                    ("debit", "!=", 0.0),
                ]
            )
            credit = sum(move_lines.mapped("amount_residual")) or 0.0
            warehouse_config = partner.res_warehouse_ids.filtered(
                lambda wh_conf: wh_conf.warehouse_id.id == current_warehouse
            )
            # If a warehouse configuration doesn't exist then it must assume
            # that credit limit in this warehouse is cero and allowed
            # only cash sales.
            if not warehouse_config:
                partner.credit_overloaded = True
            else:
                credit_limit = warehouse_config.credit_limit
                new_credit = credit + new_amount_currency
                partner.credit_overloaded = new_credit > credit_limit

    def _get_overdue_credit(self):
        for partner in self:
            context = self.env.context or {}
            current_journal = context.get("journal_id", False)
            current_warehouse = context.get("warehouse_id", False)
            journals_sale_team = self.sale_team_journals(current_warehouse, current_journal)
            if not current_warehouse:
                # We have to search the sale team that has the journal_id in
                # journal_team_ids to obtain its default_warehouse
                default_sale_team = self.env["account.journal"].browse(current_journal).section_id
                current_warehouse = default_sale_team.default_warehouse.id
            warehouse_config = partner.res_warehouse_ids.filtered(
                lambda wh_conf: wh_conf.warehouse_id.id == current_warehouse
            )
            acc_partner = self.env["res.partner"]._find_accounting_partner(partner)
            movelines = self.env["account.move.line"].search(
                [
                    ("partner_id", "=", acc_partner.id),
                    ("account_id.internal_type", "=", "receivable"),
                    ("move_id.state", "!=", "draft"),
                    ("reconciled", "=", False),
                    ("journal_id", "in", journals_sale_team),
                ]
            )
            debit_maturity, credit_maturity = 0.0, 0.0
            for line in movelines:
                # Allow sale if a partner has the warehouse configuration with
                # allow_overdue_invoice True
                if not warehouse_config or not warehouse_config.allow_overdue_invoice:
                    if line.date_maturity:
                        limit_day = line.date_maturity
                    else:
                        limit_day = fields.Date.today()
                    if limit_day <= fields.Date.today():
                        # credit and debit maturity sums all aml
                        # with late payments
                        debit_maturity += line.amount_residual if line.debit else 0.0
                    if line.credit and line.reconciled:
                        credit_maturity += line.amount_residual if line.amount_residual > 0.0 else 0.0
                    else:
                        credit_maturity += line.credit
            balance_maturity = debit_maturity - credit_maturity
            partner.overdue_credit = balance_maturity > 0.0

    @api.depends("credit_overloaded", "overdue_credit", "credit_limit")
    def get_allowed_sale(self):
        return super().get_allowed_sale()
