
from .common import TestTypStock


class TestPedimentoProductWizard(TestTypStock):

    def setUp(self):
        """Define Global variables to tests
        """
        super(TestPedimentoProductWizard, self).setUp()

        # get the objects
        self.wizard_pedimento = self.env['pedimento.product']
        self.production_lot = self.env['stock.production.lot']
        self.landed_cost = self.env['stock.landed.cost']
        self.stock_quant = self.env['stock.quant']
        self.product_id = self.env.ref('typ_stock.product_test_01')
        self.location_id = self.env.ref('stock.stock_location_components')
        self.journal_id = self.env.ref('account.expenses_journal')
        self.partner_id = self.env.ref('base.res_partner_23')
        self.product_id.update({'track_incoming': True,
                                'track_outgoing': True,
                                'landed_cost_ok': True,
                                })
        self.quant = self.stock_quant.create({
            'product_id': self.product_id.id,
            'qty': 3.00,
            'location_id': self.location_id.id,
            'cost': 80.00,
        })
        self.serial = self.production_lot.create({
            'name': '00003',
            'product_id': self.product_id.id,
            'last_location_id': self.location_id.id,
            'ref': '00003',
        })
        self.landed = self.landed_cost.create({
            'name': '15  48  3009  0001234',
            'is_pedimento': True,
            'account_journal_id': self.journal_id.id,
            'broker_id': self.partner_id.id,
        })
        self.context = {'active_id': self.quant.id}

    # Methods of test
    def test_00_test_wizard_pedimento_product(self):

        # The wizard is executed and no value is assigned so both variables are
        # null
        wizard = self.wizard_pedimento.with_context(self.context).create({})
        wizard.write_lot_in_quant()
        self.assertEqual(self.quant.lot_id.id, False)
        self.assertEqual(self.quant.landed_id.id, False)

        # test wizard if select only lot_id
        wizard = self.wizard_pedimento.with_context(self.context).create({
            'lot_id': self.serial.id,
        })
        wizard.write_lot_in_quant()
        self.assertEqual(self.quant.lot_id.id, self.serial.id)
        self.assertEqual(self.quant.landed_id.id, False)

        # test wizard if select only landed_id
        wizard = self.wizard_pedimento.with_context(self.context).create({
            'landed_id': self.landed.id,
        })
        wizard.write_lot_in_quant()
        self.assertEqual(self.quant.lot_id.id, self.serial.id)
        self.assertEqual(self.quant.landed_id.id, self.landed.id)

        # test wizard if no select The wizard is executed and no value is
        # assigned, the variables hold the previously loaded value
        wizard = self.wizard_pedimento.with_context(self.context).create({})
        wizard.write_lot_in_quant()
        self.assertEqual(self.quant.lot_id.id, self.serial.id)
        self.assertEqual(self.quant.landed_id.id, self.landed.id)
