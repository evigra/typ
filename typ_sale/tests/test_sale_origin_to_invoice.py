from odoo.tests.common import TransactionCase


class TestSaleOriginToInvoice(TransactionCase):

    def setUp(self):
        super(TestSaleOriginToInvoice, self).setUp()

        self.product = self.env.ref('product.product_product_6')
        self.partner = self.env.ref('base.res_partner_1')

        self.sale_order = self.env['sale.order'].with_context(
            tracking_disable=True).create({
                'partner_id': self.partner.id,
            })
        sale_line = self.env['sale.order.line'].with_context(
            tracking_disable=True)
        self.sol_prod_order = sale_line.create({
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 5,
            'product_uom': self.product.uom_id.id,
            'price_unit': self.product.list_price,
            'order_id': self.sale_order.id,
        })

        # Context
        self.context = {
            'active_model': 'sale.order',
            'active_ids': [self.sale_order.id],
            'active_id': self.sale_order.id,
        }

    def set_quantities_location(self, location, quantity):
        self.env['stock.quant'].create({
            'location_id': location.id,
            'product_id': self.product.id,
            'quantity': quantity,
        })

    def test_00_invoice_one_origin(self):
        """ Test origin in invoice with name of pickings to customer
        destination related"""

        self.sale_order.action_confirm()
        pick = self.sale_order.picking_ids

        self.set_quantities_location(pick.location_id, 5.0)

        pick.action_assign()
        pick.move_lines.write({'quantity_done': 5})
        pick.button_validate()

        # Let's do an invoice with invoiceable lines
        payment = self.env['sale.advance.payment.inv'].with_context(
            self.context).create({
                'advance_payment_method': 'delivered'
            })
        payment.create_invoices()
        invoice = self.sale_order.invoice_ids[0]
        invoice.action_invoice_open()

        origin = "%s : %s" % (self.sale_order.name, pick.name)
        self.assertEqual(invoice.origin, origin)

    def test_01_invoice_multi_origin(self):
        """ Test origin in invoice with name of pickings to customer
        destination related. And there are multi sale orders as origin"""

        sale_one = self.sale_order
        sale_one.action_confirm()
        pick_one = sale_one.picking_ids

        self.set_quantities_location(pick_one.location_id, 5.0)

        pick_one.action_assign()
        pick_one.move_lines.write({'quantity_done': 5})
        pick_one.button_validate()

        sale_two = self.sale_order.copy()
        sale_two.action_confirm()
        pick_two = sale_two.picking_ids

        self.set_quantities_location(pick_two.location_id, 5.0)

        pick_two.action_assign()
        pick_two.move_lines.write({'quantity_done': 5})
        pick_two.button_validate()

        # Let's do an invoice with invoiceable lines
        self.context.update({
            'active_ids': [sale_one.id, sale_two.id],
            })
        payment = self.env['sale.advance.payment.inv'].with_context(
            self.context).create({
                'advance_payment_method': 'delivered'
            })
        payment.create_invoices()
        invoice = self.sale_order.invoice_ids[0]
        invoice.action_invoice_open()

        origins = "%s : %s, %s : %s" % (sale_one.name, pick_one.name,
                                        sale_two.name, pick_two.name)
        self.assertEqual(invoice.origin, origins)
