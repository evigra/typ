import odoo
from .common import TestPointOfSaleCommon


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestPosSaleTeam(TestPointOfSaleCommon):

    def test_10_saleteam_invoice(self):
        """Test to validate invoice's team configured from the pos config"""

        # create a new team
        self.team = self.env['crm.team'].create({
            'name': 'Team Test',
        })
        # configure the session
        self.pos_config.write({
            'crm_team_id': self.team.id
        })

        self.pos_order_pos1 = self.pos_order.create(self.dict_vals)

        # To click on the "Make Payment" wizard to pay the PoS order
        context_make_payment = {
            "active_ids": [self.pos_order_pos1.id],
            "active_id": self.pos_order_pos1.id}
        pos_payment = self.pos_make_payment.with_context(
            context_make_payment).create({
                'amount': (450 * 2 + 300 * 3)
            })
        # To click on the validate button to register the payment.
        context_payment = {'active_id': self.pos_order_pos1.id}
        pos_payment.with_context(context_payment).check()

        # generate an invoice from the order
        res = self.pos_order_pos1.action_pos_order_invoice()

        # test that the team of the invoice is correct
        invoice = self.env['account.invoice'].browse(res['res_id'])
        self.assertEqual(invoice.team_id, self.team,
                         "Session not configured with the sales team")
