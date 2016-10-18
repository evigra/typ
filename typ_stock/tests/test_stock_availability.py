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
        self.test_wh = self.env.ref(
            'default_warehouse_from_sale_team.stock_warehouse_default_team'
        )

        self.payment_term = self.env.ref(
            'account.account_payment_term_immediate')

    def test_10_validation_not_allow_negative_numbers(self):
        """Validate to warehouses to not allow negative numbers in product
           availability
        """
        demo_user = self.env.ref('base.user_demo')

        sale = self.sale_obj.sudo(demo_user).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': self.test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
                'product_uom': self.product.uom_id.id,
            })],
            'payment_term': self.payment_term.id,
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

    def test_20_validation_not_allow_amount_availability(self):
        """Restrict the amounts, when greater than availability
        """
        demo_user = self.env.ref('base.user_demo')

        sale = self.sale_obj.sudo(demo_user).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': self.test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 5.0,
                'price_unit': 100.0,
                'product_uom': self.product.uom_id.id,
            })],
            'payment_term': self.payment_term.id,
        })

        # Confirm sale order
        sale.sudo(demo_user).action_button_confirm()

        pickings = sale.picking_ids.filtered(
            lambda picking: 'OUT' in picking.name)

        # Availability 5 products
        self.quant = self.env['stock.quant'].create({
            'location_id': pickings[0].location_id.id,
            'product_id': self.product.id,
            'qty': 5.0,
        })

        # Assign availability
        pickings[0].sudo(demo_user).action_assign()
        context = {
            'active_model': "stock.picking",
            'active_ids': [pickings[0].id],
            'active_id': pickings[0].id,
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": pickings.ids[0], }
            )
        wizard_transfer_id.item_ids[0].write({'quantity': 10})
        msg = 'Negative Quant creation error. Contact personnel ' \
            'Vauxoo immediately'
        with self.assertRaisesRegexp(UserError, msg):
            wizard_transfer_id.do_detailed_transfer()

    def test_30_validation_return_customer_amount(self):
        """Restrict the returned quantity, when greater than invoiced from sale
        order
        """
        self.return_obj = self.env['stock.return.picking']
        demo_user = self.env.ref('base.user_demo')

        # Stockable Product
        self.product.write({'type': 'product'})

        sale = self.sale_obj.sudo(demo_user).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': self.test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 7.0,
                'price_unit': 100.0,
                'product_uom': self.product.uom_id.id,
            })],
            'payment_term': self.payment_term.id,
        })

        # Confirm sale order
        sale.sudo(demo_user).action_button_confirm()

        pickings = sale.picking_ids.filtered(
            lambda picking: 'OUT' in picking.name)

        # Availability 7 products
        self.quant = self.env['stock.quant'].create({
            'location_id': pickings[0].location_id.id,
            'product_id': self.product.id,
            'qty': 7.0,
        })

        # Assign availability
        pickings[0].sudo(demo_user).action_assign()

        context = {
            'active_model': "stock.picking",
            'active_ids': [pickings[0].id],
            'active_id': pickings[0].id,
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": pickings.ids[0], }
            )
        # Done picking out customer
        wizard_transfer_id.sudo(demo_user).do_detailed_transfer()

        # Start return
        wizard_return_id = self.return_obj.with_context(
            context).sudo(demo_user).create({})

        # Return 10 products
        wizard_return_id.product_return_moves[0].write({'quantity': 10})

        msg = "The return of the product %s, exceeds the amount invoiced" % \
            (self.product.name)
        with self.assertRaisesRegexp(UserError, msg):
            wizard_return_id.create_returns()

    def test_40_validation_return_customer_duplicate(self):
        """Restrict picking duplicate for return
        order
        """
        self.return_obj = self.env['stock.return.picking']
        demo_user = self.env.ref('base.user_demo')

        # Stockable Product
        self.product.write({'type': 'product'})

        sale = self.sale_obj.sudo(demo_user).create({
            'name': 'Tests Main Sale Order',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': self.test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 7.0,
                'price_unit': 100.0,
                'product_uom': self.product.uom_id.id,
            })],
            'payment_term': self.payment_term.id,
        })

        # Confirm sale order
        sale.sudo(demo_user).action_button_confirm()

        pickings = sale.picking_ids.filtered(
            lambda picking: 'OUT' in picking.name)

        # Availability 7 products
        self.quant = self.env['stock.quant'].create({
            'location_id': pickings[0].location_id.id,
            'product_id': self.product.id,
            'qty': 7.0,
        })

        # Assign availability
        pickings[0].sudo(demo_user).action_assign()

        context = {
            'active_model': "stock.picking",
            'active_ids': [pickings[0].id],
            'active_id': pickings[0].id,
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": pickings.ids[0], }
            )
        # Done picking out customer
        wizard_transfer_id.sudo(demo_user).do_detailed_transfer()

        # Start return
        wizard_return_id = self.return_obj.with_context(
            context).sudo(demo_user).create({})

        # Return 7 products
        wizard_return_id.sudo(demo_user).create_returns()

        # Return 7 products again
        msg = "The return of the product %s, exceeds the amount invoiced" % \
            (self.product.name)
        with self.assertRaisesRegexp(UserError, msg):
            wizard_return_id.sudo(demo_user).create_returns()
