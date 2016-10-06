# coding: utf-8

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class TestStockAvailability(TransactionCase):

    def setUp(self):
        super(TestStockAvailability, self).setUp()
        self.transfer_obj = self.env['stock.transfer_details']
        self.sale_obj = self.env['sale.order']
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_9')
        self.product = self.env.ref('typ_stock.product_product_whead')

    def test_10_validation_not_allow_negative_numbers(self):
        """Validate to warehouses to not allow negative numbers in product
           availability
        """
        demo_user = self.env.ref('base.user_demo')
        test_wh = self.env.ref(
            'default_warehouse_from_sale_team.stock_warehouse_default_team'
        )

        payment_term = self.env.ref('account.account_payment_term_immediate')

        sale = self.sale_obj.sudo(demo_user).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
                'product_uom': self.product.uom_id.id,
            })],
            'payment_term': payment_term.id,
        })

        # Confirm sale order
        sale.sudo(demo_user).action_button_confirm()
        pickings = sale.picking_ids.filtered(
            lambda picking: 'OUT' in picking.name)

        # Verify availability
        pickings.sudo(demo_user).action_confirm()
        # Force availability
        pickings.sudo(demo_user).force_assign()
        context = {
            'active_model': "stock.picking",
            'active_ids': [pickings.ids[0]],
            'active_id': pickings.ids[0],
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": pickings.ids[0], }
            )

        msg = 'Negative Quant creation error. Contact personnel ' \
            'Vauxoo immediately'
        with self.assertRaisesRegexp(UserError, msg):
            wizard_transfer_id.do_detailed_transfer()