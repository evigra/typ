# coding: utf-8

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class TestStockAvailability(TransactionCase):

    def setUp(self):
        super(TestStockAvailability, self).setUp()
        self.transfer_obj = self.env['stock.transfer_details']
        self.picking_obj = self.env['stock.picking']
        self.sale_obj = self.env['sale.order']
        self.company = self.env.ref('base.main_company')
        self.partner = self.env.ref('base.res_partner_9')
        self.product = self.env.ref('typ_stock.product_product_whead')
        self.product_deluxe = self.env.ref(
            'typ_stock.product_product_whead_deluxe')
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

        msg = 'Negative Quant creation error of the product %s. ' \
            'Contact Vauxoo personnel immediately' % (self.product.name)
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
        msg = 'Negative Quant creation error of the product %s. ' \
            'Contact Vauxoo personnel immediately' % (self.product.name)
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

    def create_picking(self, picking_type, source_location, dest_location,
                       qty):
        """Create picking for receipt and delivery product

        :param picking_type: Type of the picking to create
        :type picking_type: stock.picking.type()
        :param source_location: Origin of the products to move
        :type source_location: stock.location()
        :param dest_location: stock.location()
        :param qty: Quantity of the product to move
        :type qty: float

        :return: All required fields to create a picking
        :rtype: dict
        """
        move = {
            'product_uom_qty': qty,
            'product_id': self.product.id,
            'location_id': source_location.id,
            'location_dest_id': dest_location.id,
            'product_uom': self.product.uom_id.id,
            'name': 'Test Move',
            'state': 'confirmed',
        }
        picking = {
            'picking_type_id': picking_type.id,
            'state': 'confirmed',
            'warehouse_id': self.test_wh.id,
            'move_type': 'direct',
            'invoice_state': 'none',
            'move_lines': [(0, 0, move)],
        }

        pick = self.picking_obj.create(picking)
        # Confirm Pickings
        pick.action_confirm()
        # Reserving lines
        pick.action_assign()
        return pick

    def test_50_validate_quant_reservation(self):
        """Validate the correct creation and reservation of the quants avoiding
        reserve quants if theses are already reserved
        """

        self.product.write({'type': 'product'})
        v_qty = self.product.virtual_available
        source = self.env.ref('stock.stock_location_suppliers')
        dest = self.env.ref('stock.stock_location_stock')
        ptype = self.env.ref('stock.picking_type_in')
        # Receipt product
        pick = self.create_picking(ptype, source, dest, 100)
        value = self.transfer_obj.\
            with_context({'active_model': 'stock.picking',
                          'active_id': pick.id,
                          'active_ids': [pick.id]}).\
            default_get([])
        line = []
        for ope in value.get('item_ids', []):
            line.append((0, 0, ope))

        value['item_ids'] = line
        value['picking_id'] = pick.id
        # Creating an object of the pack window
        trans_id = self.transfer_obj.create(value)
        for item in trans_id.item_ids:
            item.quantity = item.expected_quantity
        # Validating wizard
        trans_id.do_detailed_transfer()
        self.assertEqual(pick.state, 'done', 'The pick was not validated')
        # Check qty
        vqty = v_qty + 100
        self.assertEqual(vqty, self.product.virtual_available,
                         'The virtual available is wrong')
        # Reserve and Delivery
        qty = vqty - 10

        source = self.env.ref('stock.stock_location_stock')
        dest = self.env.ref('stock.stock_location_customers')
        ptype = self.env.ref('stock.picking_type_out')
        # Create picking with qty available
        pick1 = self.create_picking(ptype, source, dest, qty)
        # Check qty
        self.assertEqual(10, self.product.virtual_available,
                         'The virtual available is wrong')
        # Create picking with more thant available
        pick2 = self.create_picking(ptype, source, dest, 10)

        value = self.transfer_obj.\
            with_context({'active_model': 'stock.picking',
                          'active_id': pick2.id,
                          'active_ids': [pick2.id]}).\
            default_get([])
        line = []
        for ope in value.get('item_ids', []):
            ope.update({'quantity': 15})
            line.append((0, 0, ope))

        value['item_ids'] = line
        value['picking_id'] = pick2.id
        # Creating an object of the pack window
        trans_id = self.transfer_obj.create(value)
        msg = 'Negative Quant creation error of the product %s. ' \
            'Contact Vauxoo personnel immediately' % (self.product.name)
        # The picking cannot be validated
        with self.assertRaisesRegexp(UserError, msg):
            trans_id.do_detailed_transfer()

        value = self.transfer_obj.\
            with_context({'active_model': 'stock.picking',
                          'active_id': pick1.id,
                          'active_ids': [pick1.id]}).\
            default_get([])
        line = []
        for ope in value.get('item_ids', []):
            line.append((0, 0, ope))

        value['item_ids'] = line
        value['picking_id'] = pick1.id
        # Creating an object of the pack windontw
        trans_id = self.transfer_obj.create(value)
        # Validating wizard
        trans_id.do_detailed_transfer()

    def test_60_validation_return_customer_distinct_sale(self):
        """Restrict the returned quantity, when a sale is made, a return, then
        makes another sale of that same product and then returns the first sale
        again
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
                'product_uom': self.product.uom_id.id, }),
                (0, 0, {
                    'product_id': self.product_deluxe.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 200.0,
                    'product_uom': self.product_deluxe.uom_id.id,
                })],
            'payment_term': self.payment_term.id,
        })

        # Confirm sale order
        sale.sudo(demo_user).action_button_confirm()

        pickings = sale.picking_ids.filtered(
            lambda picking: 'OUT' in picking.name)

        # Adding availability 7 products
        self.quant = self.env['stock.quant'].create({
            'location_id': pickings[0].location_id.id,
            'product_id': self.product.id,
            'qty': 7.0,
        })

        # Adding availability 1 product
        self.quant = self.env['stock.quant'].create({
            'location_id': pickings[0].location_id.id,
            'product_id': self.product_deluxe.id,
            'qty': 1.0,
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

        wizard_return_id.create_returns()

        pickings_returned = sale.picking_ids.filtered(
            lambda picking: 'IN' in picking.name)

        # Assign availability to picking returned
        pickings_returned[0].sudo(demo_user).action_assign()

        context = {
            'active_model': "stock.picking",
            'active_ids': [pickings_returned[0].id],
            'active_id': pickings_returned[0].id,
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": pickings_returned.ids[0], }
            )

        # Done picking returned
        wizard_transfer_id.sudo(demo_user).do_detailed_transfer()

        # Create second sale order
        sale_second = self.sale_obj.sudo(demo_user).create({
            'name': 'Tests Main Sale Order duplicated',
            'company_id': self.company.id,
            'partner_id': self.partner.id,
            'warehouse_id': self.test_wh.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 7.0,
                'price_unit': 100.0,
                'product_uom': self.product.uom_id.id, }),
                (0, 0, {
                    'product_id': self.product_deluxe.id,
                    'product_uom_qty': 1.0,
                    'price_unit': 200.0,
                    'product_uom': self.product_deluxe.uom_id.id,
                })],
            'payment_term': self.payment_term.id,
        })

        # Confirm second sale order
        sale_second.sudo(demo_user).action_button_confirm()

        pickings_second = sale_second.picking_ids.filtered(
            lambda picking: 'OUT' in picking.name)

        # Assign availability in picking of sale second
        pickings_second[0].sudo(demo_user).action_assign()

        context = {
            'active_model': "stock.picking",
            'active_ids': [pickings_second[0].id],
            'active_id': pickings_second[0].id,
            }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": pickings_second.ids[0], }
            )

        # Done picking out customer
        wizard_transfer_id.sudo(demo_user).do_detailed_transfer()

        # Return picking of first sale order again

        wizard_return_id.product_return_moves.filtered(
            lambda dat: dat.product_id == self.product_deluxe).unlink()

        msg = "The return of the product %s, exceeds the amount invoiced" % \
            (self.product.name)
        with self.assertRaisesRegexp(UserError, msg):
            wizard_return_id.create_returns()
