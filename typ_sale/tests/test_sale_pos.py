# -*- coding: utf-8 -*-

from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestSaleOrderPos(common.TransactionCase):

    def setUp(self):

        super(TestSaleOrderPos, self).setUp()
        # get the objects
        self.partner = self.env.ref('base.res_partner_9')
        self.warehouse = self.env.ref('typ_sale.wh_01')
        self.transfer_obj = self.env['stock.transfer_details']
        self.invoice_onshipping_obj = self.env['stock.invoice.onshipping']
        self.pay_method_id = self.env.ref(
            'l10n_mx_payment_method.pay_method_efectivo')
        self.acc_payment = self.env.ref('account_payment.partner_bank_1')
        self.sale_team = self.env.ref('typ_sale.sale_team_01')
        self.group_inv_without_ped = self.env.ref(
            'typ_sale.group_invoiced_without_pedimento')
        self.products = {
            'product_order': self.env.ref('product.product_product_35'),
            'serv_order': self.env.ref('product.product_product_consultant'),
        }

        # setting values to sale order
        self.dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pos': True,
            'order_policy': 'picking',
            'warehouse_id': self.warehouse.id,
            'pay_method_id': self.pay_method_id.id,
            'acc_payment': self.acc_payment.id,
            'section_id': self.sale_team.id,
            'carrier_id': False}

        self.dict_vals_line = [{
            'name': p.name, 'product_id': p.id, 'product_uom_qty': 1,
            'product_uom': p.uom_id.id, 'price_unit': p.list_price
            } for (_, p) in self.products.items()]

        self.dict_vals.update({
            'order_line':  [(0, 0, ope) for ope in self.dict_vals_line]
        })

        # Availability 3 products
        self.quant = self.env['stock.quant'].create({
            'location_id': self.warehouse.wh_input_stock_loc_id.id,
            'product_id': self.products['product_order'].id,
            'qty': 0,
        })

    def create_sale(self):
        """Create sale order"""

        # Create Order Pos
        sale_pos = self.env['sale.order'].create(self.dict_vals)
        sale_pos.action_button_confirm()

        return sale_pos

    # Methods of tests
    def test_01_picking_confirmed_availability(self):
        """Picking advanced to state waiting availability automatic"""

        # Create Order Pos
        sale_pos = self.create_sale()

        # Check state of picking on sale order pos
        self.assertEqual(sale_pos.picking_ids.state, 'confirmed',
                         'Picking with quant negative')

    def test_02_picking_assigned_with_insufficient_product(self):
        """Picking in state partially_available with quantity availability"""

        # Availability 3 products
        self.quant.qty = 3

        # Quantity of 5 product sold
        for product in self.dict_vals_line:
            if product['product_id'] == self.products['product_order'].id:
                product['product_uom_qty'] = 5

        # Create Order Pos
        sale_pos = self.create_sale()

        # Check state of picking on sale order pos
        self.assertEqual(sale_pos.picking_ids.state, 'partially_available',
                         'Picking with quant negative')

    def test_03_picking_assign_traceability(self):
        """Picking in state assigned for unset lot number"""

        # Traceability activate
        self.products['product_order'].track_all = True

        # Availability 3 products
        self.quant.qty = 3

        # Create Order Pos
        sale_pos = self.create_sale()

        # Check state of picking on sale order pos
        self.assertEqual(sale_pos.picking_ids.state, 'assigned',
                         'Product transferred without lot number')

    def test_04_picking_done_pedimento(self):
        """Picking in state done for unset pedimento"""

        # Availability 3 products
        self.quant.qty = 3

        # Create Order Pos
        sale_pos = self.create_sale()

        # Check state of picking on sale order pos
        self.assertEqual(sale_pos.picking_ids.state, 'done',
                         'Picking not has been confirmed')

        # Check invoice from sale order pos
        self.assertFalse(sale_pos.invoice_ids.state,
                         'Invoice created incorrect')

    def test_05_onshipping_open_invoice_automatic(self):
        """Invoice automatic from picking transfered"""

        # Associate group to test user
        self.env.user.write({
            'groups_id': [(4, self.group_inv_without_ped.id)]})

        # Availability 3 products
        self.quant.qty = 3

        # Create Order Pos
        sale_pos = self.create_sale()

        # Check state of picking on sale order pos
        self.assertEqual(sale_pos.picking_ids.state, 'done',
                         'Picking not has been transfered')

        # Check invoice from sale order pos
        self.assertEqual(sale_pos.invoice_ids.state, 'draft',
                         'Invoice not created from picking')

    def test_06_sale_classic_equal_sale_pos(self):
        """Values of the sales invoice pos, compared to conventional sales"""

        # Associate group to test user
        self.env.user.write({
            'groups_id': [(4, self.group_inv_without_ped.id)]})

        # Availability 3 products
        self.quant.qty = 3

        # Create Order Pos
        sale_pos = self.create_sale()

        # Change location of quant
        self.quant.location_id = self.warehouse.lot_stock_id.id

        # Create Order Conventional
        self.dict_vals.update({'pos': False, 'name': 'Test Sale Classic'})
        sale = self.create_sale()

        sale.picking_ids.action_assign()

        context = {
            'active_model': "stock.picking",
            'active_ids': sale.picking_ids.ids,
        }

        wizard_transfer_id = self.transfer_obj.with_context(context).create(
            {"picking_id": sale.picking_ids.id})
        wizard_transfer_id.do_detailed_transfer()

        inv_shipping = self.invoice_onshipping_obj.with_context(
            active_model="stock.picking",
            active_ids=sale.picking_ids.ids).create({})
        inv_shipping.create_invoice()

        # Invoice from sale order pos
        invoice_pos = sale_pos.invoice_ids

        # Invoice from sale order conventional
        invoice = sale.invoice_ids

        # Check journal on invoice from pos
        self.assertEqual(invoice_pos.journal_id,
                         invoice.journal_id,
                         'Journal on invoice not set by default')

        # Check type journal on invoice from pos
        self.assertEqual(invoice_pos.journal_id.type,
                         invoice.journal_id.type,
                         'Journal type on invoice not set by default')

        # Check type payment term on invoice from pos
        self.assertEqual(invoice_pos.type_payment_term,
                         invoice.type_payment_term,
                         'Type of payment term on invoice not set by default')

        # Check address on invoice from pos
        self.assertEqual(invoice_pos.address_issued_id,
                         invoice.address_issued_id,
                         'Address on invoice not set by partner correct')

        # Check amount total on invoice from pos
        self.assertEqual(
            invoice_pos.amount_total, invoice.amount_total,
            'Amount Total on invoice not set correct with sale pos')

        # Check products on invoice from pos
        self.assertEqual(
            len(invoice_pos.invoice_line), len(invoice.invoice_line),
            'The products invoiced deferred the order pos')

        # Check pay method on invoice from pos
        self.assertEqual(
            invoice_pos.pay_method_id, invoice.pay_method_id,
            'Payment method on invoice not set correct with sale pos')

        # Check account number on invoice from pos
        self.assertEqual(
            invoice_pos.acc_payment, invoice.acc_payment,
            'Account Number on invoice not set correct with sale pos')

        # Check amount untaxed on invoice from pos
        self.assertEqual(
            invoice_pos.amount_untaxed, invoice.amount_untaxed,
            'Subtotal on invoice not set correct with sale pos')

        # Check amount tax on invoice from pos
        self.assertEqual(
            invoice_pos.amount_tax, invoice.amount_tax,
            'Tax on invoice not set correct with sale pos')

        # Check salesperson on invoice from pos
        self.assertEqual(
            invoice_pos.user_id, invoice.user_id,
            'Salesperson on invoice not set correct with sale pos')

        # Check sales team on invoice from pos
        self.assertEqual(
            invoice_pos.section_id, invoice.section_id,
            'Sales Team on invoice not set correct with sale pos')
