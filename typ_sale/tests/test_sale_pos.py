# -*- coding: utf-8 -*-

from openerp.tests import common


@common.at_install(False)
@common.post_install(True)
class TestSaleOrderPos(common.TransactionCase):

    def setUp(self):

        super(TestSaleOrderPos, self).setUp()
        # get the objects
        self.partner = self.env.ref('base.res_partner_9')
        self.product = self.env.ref('product.product_product_35')
        self.warehouse = self.env.ref('typ_sale.wh_01')
        self.location = self.env.ref('stock.stock_location_company')
        self.pay_method_id = self.env.ref(
            'l10n_mx_payment_method.pay_method_efectivo')
        self.acc_payment = self.env.ref('account_payment.partner_bank_1')
        self.sale_team = self.env.ref('typ_sale.sale_team_01')
        self.group_inv_without_ped = self.env.ref(
            'typ_sale.group_invoiced_without_pedimento')

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

        self.dict_vals_line = {
            'name': self.product.name, 'product_id': self.product.id,
            'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
            'price_unit': 100, }

        self.dict_vals.update({
            'order_line': [(0, 0, self.dict_vals_line)],
        })

        # Availability 3 products
        self.quant = self.env['stock.quant'].create({
            'location_id': self.warehouse.wh_input_stock_loc_id.id,
            'product_id': self.product.id,
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
        self.dict_vals_line.update({'product_uom_qty': 5})

        # Create Order Pos
        sale_pos = self.create_sale()

        # Check state of picking on sale order pos
        self.assertEqual(sale_pos.picking_ids.state, 'partially_available',
                         'Picking with quant negative')

    def test_03_picking_assign_traceability(self):
        """Picking in state assigned for unset lot number"""

        # Traceability activate
        self.product.track_all = True

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
