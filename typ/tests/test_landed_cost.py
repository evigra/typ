from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("landed_cost")
class TestLandedCost(TypTransactionCase):
    def create_cost_guide(
        self,
        name="Guide 1",
        partner=None,
        journal=None,
        guide_date=None,
        reference="charged",
        currency=None,
        company=None,
        create_line=True,
        **line_kwargs
    ):
        if partner is None:
            partner = self.vendor
        if journal is None:
            journal = self.journal_expense
        if guide_date is None:
            guide_date = self.today
        guide = Form(self.env["stock.landed.cost.guide"])
        guide.name = name
        guide.partner_id = partner
        guide.journal_id = journal
        guide.date = guide_date
        guide.reference = reference
        guide.comments = "Guide comments"
        if currency is not None:
            guide.currency_id = currency
        if company is not None:
            guide.company_id = company
        guide = guide.save()
        if create_line:
            self.create_guide_line(guide, **line_kwargs)
        return guide

    def create_guide_line(self, guide, product=None, cost=150, freight_type="services"):
        if product is None:
            product = self.product_cost
        with Form(guide) as gd, gd.line_ids.new() as line:
            line.product_id = product
            line.cost = cost
            line.freight_type = freight_type

    def create_landed_cost(self, guide=None, cost_date=None):
        landed_cost = Form(self.env["stock.landed.cost"])
        if cost_date is not None:
            landed_cost.date = cost_date
        if guide is not None:
            # Adding existing records to o2m is not natively supported yet, so we do it manually
            landed_cost._values["guide_ids"].append((4, guide.id, False))
            landed_cost._perform_onchange(["guide_ids"])
        landed_cost = landed_cost.save()
        return landed_cost

    def create_invoice_from_guide(self, guides, journal=None):
        if journal is None:
            journal = self.journal_bills
        ctx = {
            "active_model": guides._name,
            "active_ids": guides.ids,
            "active_id": guides[0].id,
        }
        wizard = Form(self.env["invoice.guides"].with_context(**ctx))
        wizard.journal_id = journal
        wizard = wizard.save()
        wizard_res = wizard.create_invoice()
        invoice = self.env[wizard_res["res_model"]].browse(wizard_res["res_id"])
        return invoice

    def test_01_guide_flow(self):
        """Test creating & validating a cost guide, ensuring a journal entry is created"""
        # Create guide
        guide = self.create_cost_guide()
        self.assertRecordValues(
            guide,
            [
                {
                    "state": "draft",
                    "landed": False,
                    "invoiced": False,
                },
            ],
        )

        # Validate guide
        guide.action_valid()
        self.assertEqual(guide.state, "valid")

        # Check a journal entry was created
        self.assertRecordValues(
            guide.move_id,
            [
                {
                    "move_type": "entry",
                    "state": "posted",
                    "amount_total": 150.0,
                    "ref": "charged",
                    "journal_id": self.journal_expense.id,
                }
            ],
        )
        self.assertEqual(guide.account_move_name, guide.move_id.name)

        # Create invoice from guide
        invoice = self.create_invoice_from_guide(guide)
        self.assertRecordValues(
            records=invoice.invoice_line_ids,
            expected_values=[
                {
                    "product_id": self.product_cost.id,
                    "quantity": 1.0,
                    "price_unit": 150.0,
                    "guide_line_id": guide.line_ids.id,
                }
            ],
        )
        self.assertTrue(guide.invoiced)

        # We shouldn't be able to invoice again
        error_msg = "The following guides are already invoiced"
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.create_invoice_from_guide(guide)

        # Open stock accruals
        aml_credit = guide.move_id.line_ids.filtered("credit")
        self.assertEqual(aml_credit.credit, 150)
        action_accrual = guide.view_accrual()
        amls_on_accrual = self.env[action_accrual["res_model"]].search(action_accrual["domain"])
        self.assertEqual(amls_on_accrual, aml_credit + invoice.invoice_line_ids)

        # When already validated, we shouldn't be able to delete it
        error_msg = "cannot be removed when it is/was validated"
        with self.assertRaisesRegex(ValidationError, error_msg):
            guide.unlink()

        # Create a landed cost and attach the guide to it, cost lines should be automatically created
        landed_cost = self.create_landed_cost(guide=guide)
        self.assertRecordValues(
            landed_cost.cost_lines,
            [
                {
                    "product_id": self.product_cost.id,
                    "price_unit": 150,
                    "split_method": "by_current_cost_price",
                    "segmentation_cost": "landed_cost",
                },
            ],
        )

        # Once the guide has a landed cost, we should be able to cancel it, but not resetting it to draft
        guide.action_cancel()
        self.assertEqual(guide.state, "cancel")
        error_msg = "You cannot reset this guide to draft while it is associated to a Landed Cost"
        with self.assertRaisesRegex(ValidationError, error_msg):
            guide.action_draft()

    def test_02_validate_wo_lines(self):
        """Try to validate a guide without lines"""
        guide = self.create_cost_guide(create_line=False)
        error_msg = "Please create some guide lines before validating this document."
        with self.assertRaisesRegex(UserError, error_msg):
            guide.action_valid()

    def test_03_invoice_guide_diff_partner(self):
        """Try to invoice cost guides that have different partners"""
        guides = self.create_cost_guide() + self.create_cost_guide(partner=self.customer)
        error_msg = "All selected guides must have the same partner."
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.create_invoice_from_guide(guides)

    def test_04_invoice_guide_diff_currency(self):
        """Try to invoice cost guides that have different currencies"""
        guides = self.create_cost_guide() + self.create_cost_guide(currency=self.usd)
        error_msg = "All selected guides must have the same currency."
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.create_invoice_from_guide(guides)

    def test_05_invoice_guide_diff_company(self):
        """Try to invoice cost guides that have different companies"""
        guides = self.create_cost_guide() + self.create_cost_guide(company=self.company_secondary)
        error_msg = "All selected guides must have the same company."
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.create_invoice_from_guide(guides)

    def test_06_invoice_guide_product_wo_account(self):
        """Try to invoice cost guide containing a product without stock input account"""
        guides = self.create_cost_guide()
        self.product_cost.categ_id.property_stock_account_input_categ_id = False
        error_msg = "Please configure a stock input account for the product '\\[LANDING\\] Landing Cost'."
        with self.assertRaisesRegex(ValidationError, error_msg):
            self.create_invoice_from_guide(guides)
