from odoo import fields
from odoo.tests import TransactionCase


class TestPointOfSale(TransactionCase):
    def setUp(self):
        super().setUp()
        self.pos_config = self.env.ref('point_of_sale.pos_config_main')
        self.partner = self.env.ref('base.res_partner_12')
        self.product = self.env.ref('product.service_order_01')
        self.pos_config.open_session_cb()
        self.session = self.pos_config.current_session_id
        self.env.user.tz = 'America/Mexico_City'

    def create_pos_order(self, partner=None, product=None, quantity=2, price=50):
        if partner is None:
            partner = self.partner
        if product is None:
            product = self.product

        amount_total = price * quantity
        order_number = '00001-007-001%s' % len(self.session.order_ids)
        ui_order_vals = {
            'to_invoice': self.pos_config.iface_invoicing,
            'data': {
                'creation_date': fields.Datetime.now(),
                'name': 'Order %s' % order_number,
                'pos_session_id': self.session.id,
                'to_invoice': self.pos_config.iface_invoicing,
                'amount_total': amount_total,
                'partner_id': partner.id,
                'amount_return': 0,
                'amount_paid': amount_total,
                'amount_tax': 0,
                'statement_ids': [[0, 0, {
                    'journal_id': self.pos_config.journal_ids[0].id,
                    'name': fields.Datetime.now(),
                    'statement_id': self.session.statement_ids[0].id,
                    'amount': amount_total,
                    'account_id': partner.property_account_receivable_id.id,
                }]],
                'lines': [[0, 0, {
                    'pack_lot_ids': [],
                    'discount': 0,
                    'id': 1,
                    'tax_ids': [[6, 0, []]],
                    'qty': quantity,
                    'price_unit': price,
                    'product_id': product.id,
                }]],
                'l10n_mx_edi_usage': 'P01',
                'pricelist_id': partner.property_product_pricelist.id,
                'sequence_number': 10,
                'user_id': self.env.uid,
                'uid': order_number,
                'fiscal_position_id': self.pos_config.default_fiscal_position_id.id,
            },
            'id': order_number,
        }

        order_ids = self.env['pos.order'].create_from_ui([ui_order_vals])
        order = self.env['pos.order'].browse(order_ids)
        self.assertTrue(order)
        return order

    def test_01_invoice_from_pos_send_email(self):
        """Test case: generate an invoice from the PoS, it should be sent automatically by e-mail"""
        self.pos_config.iface_invoicing = True
        order = self.create_pos_order()

        # Check the created invoice
        invoice = order.invoice_id
        self.assertEqual(invoice.state, 'open')
        self.assertEqual(invoice.l10n_mx_edi_pac_status, 'signed',
                         invoice.message_ids.mapped('body'))

        # Check that the invoice was sent to the customer by e-mail
        mail_text = "Here is, in attachment, your \ninvoice"
        self.assertIn(mail_text, invoice.message_ids[0].body)
        self.assertIn(self.partner, invoice.message_ids[0].partner_ids)

        # Create an invoice copying the previous one, it shouldn't be sent by e-mail
        invoice2 = invoice.copy()
        invoice2.action_invoice_open()
        self.assertEqual(invoice2.state, 'open')
        self.assertEqual(invoice2.l10n_mx_edi_pac_status, 'signed',
                         invoice2.message_ids.mapped('body'))
        self.assertNotIn(mail_text, invoice2.message_ids[0].body)
