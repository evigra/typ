from odoo.tests.common import TransactionCase


class TestInvoiceFromPurchase(TransactionCase):
    def setUp(self):
        super().setUp()
        self.cur_mxn = self.ref("base.MXN")
        self.cur_usd = self.ref("base.USD")
        self.invoice_model = self.env["account.move"]
        self.journal_model = self.env["account.journal"]
        self.team_model = self.env["crm.team"]
        self.purchase_order = self.env.ref("purchase.purchase_order_6")
        self.partner = self.purchase_order.partner_id
        self.warehouse = self.purchase_order.picking_type_id.warehouse_id

        self.journal = self.journal_model.create({"name": "Journal Test", "code": "TEST", "type": "purchase"})

        self.team = self.team_model.create(
            {
                "name": "Team Test",
                "default_warehouse": self.warehouse.id,
                "journal_team_ids": [(4, self.journal.id, None)],
            }
        )

    def test_01_change_currency_journal(self):
        """Test for validate currency and journal related to
        the purchase order"""
        self.assertEqual(self.purchase_order.currency_id.id, self.cur_mxn)
        self.purchase_order.currency_id = self.cur_usd
        self.purchase_order.button_confirm()
        invoice = self.invoice_model.with_context(default_purchase_id=self.purchase_order.id).create(
            {
                "partner_id": self.partner.id,
                "purchase_id": self.purchase_order.id,
                "currency_id": self.cur_mxn,
                "account_id": self.partner.property_account_payable_id.id,
                "type": "in_invoice",
            }
        )
        invoice._onchange_partner_id()
        self.assertEqual(invoice.currency_id.id, self.cur_usd)
        self.assertEqual(invoice.journal_id, self.journal)
