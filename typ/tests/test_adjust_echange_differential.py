# -*- coding: utf-8 -*-

# from openerp.exceptions import ValidationError
import mock
from openerp.addons.typ_landed_costs.tests import common
from openerp import fields


class TestAdjustExchangeDifferential(common.TestTypLandedCosts):

    def setUp(self):
        super(TestAdjustExchangeDifferential, self).setUp()
        self.partner = self.env.ref('base.res_partner_21')
        self.prod = self.env.ref('typ_landed_costs.'
                                 'product_adjusts_landed_cost_1')
        self.adjust_purchase = self.env.ref('typ_landed_costs.'
                                            'adjust_purchase_landed_1')
        self.trans = self.env['stock.transfer_details']
        self.stock_invoice = self.env['stock.invoice.onshipping']
        self.currency_1.rate_ids.write({'rate': 1})
        self.currency_1.write({'rate_silent': 1})
        self.currency_1.write({'base': True})

    def get_landed_values(self, diff, picking, invoice):
        """Generate dict with the values needed for create the landed to adjust costs

        :param picking: Picking that generated the invoice
        :type picking: recordset
        :param diff: Value to adjust
        :type diff: float
        :param invoice: Invoice related with the pedimento
        :typ invoice: int

        :return Values for the new landed
        :rtype dict
        """
        product = self.env.ref('typ_landed_costs.'
                               'landed_exchange_differential_product')
        journal = self.env.ref('stock_account.stock_journal').id
        account = (diff > 0 and
                   self.env.user.company_id.
                   income_currency_exchange_account_id or
                   self.env.user.company_id.
                   expense_currency_exchange_account_id)
        cost_line = {
            'product_id': product.id,
            'name': product.name,
            'account_id': account.id,
            'split_method': diff == 100 and 'equal' or 'by_current_cost_price',
            'price_unit': diff,
            'segmentation_cost': (diff == 100 and 'landed_cost' or
                                  'material_cost')

        }
        values = {
            'date': fields.Date.today(),
            'is_pedimento': diff == 100,
            'account_journal_id': journal,
            'picking_ids': [(4, picking.id)],
            'invoice_ids': [(4, invoice)],
            'cost_lines': [(0, 0,
                            cost_line)]
        }
        return values

    def create_picking_and_invoice(self):
        """Simulate the process from purchase validation to invoice creation
        returning the new documents created
        """
        # Set the rate before validate picking
        self.currency_2.rate_ids.write({'rate': 0.050})
        # Validating purchase
        self.adjust_purchase.signal_workflow('purchase_confirm')
        # Validating if the pickings exists
        self.assertTrue(self.adjust_purchase.picking_ids,
                        'The purchase order does not have pickings')
        pick = self.adjust_purchase.picking_ids.filtered(lambda a:
                                                         a.state == 'assigned')
        # Confirm Pickings
        pick.action_confirm()
        # Reserving lines
        pick.action_assign()
        # Validating From Wizard
        # Creating the pack operations
        value = self.trans.\
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
        trans_id = self.trans.create(value)
        # Validating wizard
        trans_id.do_detailed_transfer()
        self.assertEqual(pick.state, 'done', 'The pick was not validated')
        # Costs
        self.assertEqual(self.prod.standard_price, 800,
                         'The cost of the product is not correctly set')
        # Set New Rate
        self.currency_2.rate_ids.write({'rate': 0.040})
        # Create invoice
        value = self.stock_invoice.\
            with_context({'active_model': 'stock.picking',
                          'active_id': pick.id,
                          'active_ids': [pick.id]}).\
            default_get([])
        invo_id = self.stock_invoice.\
            with_context({'active_model': 'stock.picking',
                          'active_id': pick.id,
                          'active_ids': [pick.id]}).create(value)
        invoice_ids = invo_id.\
            with_context({'active_model': 'stock.picking',
                          'active_id': pick.id,
                          'active_ids': [pick.id]}).\
            create_invoice()
        # Checking if the invoice was created
        self.assertTrue(len(invoice_ids) > 0,
                        'The invoice was not created')
        return pick, invoice_ids

    @mock.patch('openerp.addons.typ_landed_costs.models.'
                'stock_landed_costs.StockLandedCost._get_landed_values')
    def test_00_adjust_from_invoice(self, mock_values):
        """Test to adjust the differential exchange from a invoice validation
        """
        self.partner.country_id = self.adjust_purchase.company_id.country_id
        pick, inv_id = self.create_picking_and_invoice()
        inv_brw = self.env['account.invoice'].browse(inv_id[0])
        mock_values.return_value = self.get_landed_values(2000, pick, False)
        inv_brw.signal_workflow('invoice_open')
        rule = self.env.ref(
            'typ_landed_costs.'
            'automated_action_adjust_exchange_differential_invoice')
        rule._process(rule, [inv_brw.id])
        # Costs
        self.assertEqual(self.prod.standard_price, 1000,
                         'The cost of the product is not correctly updated')
        # Validated that the adjust landed was created and assigned
        self.assertTrue(inv_brw.exchange_landed_ids)
        # Validating that only one adjust is created
        rule._process(rule, [inv_brw.id])
        self.assertTrue(len(inv_brw.exchange_landed_ids) == 1)

    @mock.patch('openerp.addons.typ_landed_costs.models.'
                'stock_landed_costs.StockLandedCost._get_landed_values')
    def test_00_adjust_from_pedimento(self, mock_values):
        """Test to adjust the differential exchange from a invoice validation
        """
        self.partner.country_id = self.env.ref('base.as')
        pick, inv_id = self.create_picking_and_invoice()
        inv_brw = self.env['account.invoice'].browse(inv_id[0])
        inv_brw.signal_workflow('invoice_open')
        pedimento = self.get_landed_values(100, pick, inv_brw.id)
        landed_id = self.env['stock.landed.cost'].create(pedimento)
        landed_id.compute_landed_cost()
        mock_values.return_value = self.get_landed_values(2000, pick, False)
        landed_id.button_validate()
        rule = self.env.ref('typ_landed_costs.'
                            'automated_action_adjust_exchange_differential')
        rule._process(rule, [landed_id.id])
        # Costs
        self.assertEqual(self.prod.standard_price, 1010,
                         'The cost of the product is not correctly updated')
        # Validated that the adjust landed was created and assigned
        self.assertTrue(landed_id.exchange_landed_ids)
