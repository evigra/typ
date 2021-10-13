from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("cost_guide")
class TestCostGuide(TypTransactionCase):
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

    def test_01_guide_flow(self):
        """Test creating & validating a cost guide, ensuring a journal entry is created"""
        # Create guide
        guide = self.create_cost_guide()
        self.assertEqual(guide.state, "draft")

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

    def test_02_validate_wo_lines(self):
        """Try to validate a guide without lines"""
        guide = self.create_cost_guide(create_line=False)
        error_msg = "Please create some guide lines before validating this document."
        with self.assertRaisesRegex(UserError, error_msg):
            guide.action_valid()
