# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):

    def test_00_report_language(self):
        """Purchase Order report's language depends on the partner or broker"""
        partner_en = self.env.ref('base.res_partner_1')
        partner_en.write({'lang': 'en_US'})

        broker = self.env.ref('base.res_partner_2')
        broker.write({'lang': 'en_US'})

        p_order = self.env.ref('purchase.purchase_order_6')

        # Check PO starts without specific language
        self.assertFalse(p_order.report_lang)
        self.assertFalse(p_order.partner_id.lang)
        self.assertFalse(p_order.broker_id)

        # PO with partner's language
        p_order.write({
            'partner_id': partner_en.id,
        })
        self.assertEqual(p_order.report_lang, partner_en.lang)

        # Check PO language changes with partner's language
        partner_en.write({'lang': False})
        p_order._compute_report_lang()
        self.assertFalse(p_order.report_lang)

        # Check PO change with broker's language
        p_order.write({
            'broker_id': broker.id,
        })
        p_order._compute_report_lang()
        self.assertEqual(p_order.report_lang, broker.lang)
