import odoo
from odoo.tests.common import TransactionCase


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class TestSaleInvoiceCustoms(TransactionCase):

    def setUp(self):
        super(TestSaleInvoiceCustoms, self).setUp()
        self.move = self.env['stock.move']
        self.product_3 = self.env.ref('product.product_product_3')
        self.product_4 = self.env.ref('product.product_product_4')
        self.partner_1 = self.ref('base.res_partner_1')
        self.partner_4 = self.ref('base.res_partner_4')
        self.journal_id = self.ref('typ_landed_costs.journal_bank_test')
        self.picking_type_in_id = self.ref('stock.picking_type_in')
        self.supplier_location_id = self.ref('stock.stock_location_suppliers')
        self.stock_location_id = self.ref('stock.stock_location_stock')
        self.o_expense_id = self.ref('stock_cost_segmentation.o_expense')
        self.o_income_id = self.ref('stock_cost_segmentation.o_income')

        (self.product_3 + self.product_4).write({
            'cost_method': 'fifo',
            'valuation': 'real_time',
            'property_stock_account_input': self.o_expense_id,
            'property_stock_account_output': self.o_income_id,
        })

        # Create picking incoming shipment
        self.pick_in = self.env['stock.picking'].create({
            'partner_id': self.partner_1,
            'picking_type_id': self.picking_type_in_id,
            'location_id': self.supplier_location_id,
            'location_dest_id': self.stock_location_id})
        self.move.create({
            'name': self.product_3.name,
            'product_id': self.product_3.id,
            'product_uom_qty': 50,
            'product_uom': self.product_3.uom_id.id,
            'picking_id': self.pick_in.id,
            'location_id': self.supplier_location_id,
            'location_dest_id': self.stock_location_id})
        self.move.create({
            'name': self.product_4.name,
            'product_id': self.product_4.id,
            'product_uom_qty': 100,
            'product_uom': self.product_4.uom_id.id,
            'picking_id': self.pick_in.id,
            'location_id': self.supplier_location_id,
            'location_dest_id': self.stock_location_id})

        self.dict_vals = {
            'partner_id': self.partner_4,
            'partner_invoice_id': self.partner_4,
            'partner_shipping_id': self.partner_4,
            'order_line': [
                (0, 0,
                 {'name': self.product_3.name, 'product_id': self.product_3.id,
                  'product_uom_qty': 5,
                  'product_uom': self.product_3.uom_id.id, 'price_unit': 900}),
                (0, 0,
                 {'name': self.product_4.name, 'product_id': self.product_4.id,
                  'product_uom_qty': 10,
                  'product_uom': self.product_4.uom_id.id, 'price_unit': 900})]
            }

        self.sale_order = self.env['sale.order'].with_context(
            tracking_disable=True).create(self.dict_vals)

        # Context
        self.context = {
            'active_model': 'sale.order',
            'active_ids': [self.sale_order.id],
            'active_id': self.sale_order.id,
            'tracking_disable': True,
        }

    def test_01_sale_invoice_customs(self):
        """Test customs of invoice related in the landed cost"""

        # Confirm incoming shipment.
        self.pick_in.action_confirm()
        # Transfer incoming shipment
        res_dict = self.pick_in.button_validate()
        wizard = self.env[(res_dict.get('res_model'))].browse(
            res_dict.get('res_id'))
        wizard.process()
        moves_in = self.pick_in.move_lines

        # Create landed costs
        stock_landed_cost = self.env['stock.landed.cost'].create({
            'l10n_mx_edi_customs_number': '15  48  3009  0001235',
            'account_journal_id': self.journal_id,
            'move_ids': [(6, 0, moves_in.ids)]})

        # Process Sale Order
        self.sale_order.action_confirm()
        pick_out = self.sale_order.picking_ids

        res_dict = pick_out.button_validate()
        wizard = self.env[(res_dict.get('res_model'))].browse(
            res_dict.get('res_id'))
        wizard.process()

        # Let's do an invoice with invoiceable lines
        payment = self.env['sale.advance.payment.inv'].with_context(
            self.context).create({
                'advance_payment_method': 'delivered'
            })
        payment.create_invoices()
        invoice = self.sale_order.invoice_ids[0]
        invoice.action_invoice_open()

        customs = stock_landed_cost.l10n_mx_edi_customs_number
        lines_inv = invoice.invoice_line_ids
        self.assertTrue(all([
            line.l10n_mx_edi_customs_number == customs for line in lines_inv]),
            'There is no landed cost related to origin movement')
