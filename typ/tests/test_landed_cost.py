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
        create_line=True,
        **line_kwargs
    ):
        if partner is None:
            partner = self.customer
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
