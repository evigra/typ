
import threading
import pprint
import openerp
from openerp import api
from openerp.tests import common
from .common import TestTypStock


@common.at_install(False)
@common.post_install(True)
class TestReorderingRule(TestTypStock):
    """Class define tests for Reordering Rules Wizard to
       typ_stock, write original data demo then is required run it at final"""

    def setUp(self):
        """Define Global variables to tests
        """
        super(TestReorderingRule, self).setUp()
        self.env.cr._serialized = False
        self.env.cr.autocommit(False)
        self.demo_user = self.env.ref('base.user_demo')
        self.warehouse_id = self.env.ref('typ_stock.whr_test_03')
        self.warehouse_id4 = self.env.ref('typ_stock.whr_test_04')
        self.yourcompany_id = self.env.ref('stock.warehouse0')
        self.product_id = self.env.ref('typ_stock.product_test_01')

        # get the objects
        self.sched = self.env['procurement.orderpoint.compute']
        self.proc = self.env['procurement.order']
        self.warehouse = self.env['stock.warehouse']
        self.product = self.env['product.product']
        self.location = self.env['stock.location']
        self.order_rule = self.env['stock.warehouse.orderpoint']
        self.procurement_rule = self.env['procurement.rule']
        self.stock_route = self.env['stock.location.route']
        self.wh_op = self.env.ref('typ_stock.stock_warehouse_orderpoint_1')
        self.wh_op4 = self.env.ref('typ_stock.stock_warehouse_orderpoint_2')

        self.importance = "aa"
        self.thread_excl = [thr.name for thr in threading.enumerate()]

    def get_threads(self):
        return [thread for thread in threading.enumerate()
                if thread.name.startswith('Thread-') and
                thread.name not in self.thread_excl]

    def write_data(self, procurement_data=None):
        """Save data for that the cursor used in threads of
        test read the changes"""
        self.old_values = {
            self.warehouse_id: (
                'resupply_wh_ids', self.warehouse_id.resupply_wh_ids),
            self.warehouse_id4: (
                'resupply_wh_ids', self.warehouse_id4.resupply_wh_ids),
            self.wh_op: ('location_id', self.wh_op.location_id),
            self.wh_op4: ('location_id', self.wh_op4.location_id),
            self.product_id: ('route_ids', self.product_id.route_ids),
        }
        with openerp.api.Environment.manage():
            with openerp.registry(self.env.cr.dbname).cursor() as newcr:
                newenv = api.Environment(newcr, self.env.uid, self.env.context)
                # Add resupply warehouse to warehouse of test & location id
                # to reordering rule
                self.warehouse_id.with_env(newenv).write({
                    'resupply_wh_ids': [(6, 0, [self.yourcompany_id.id])]})
                self.warehouse_id4.with_env(newenv).write({
                    'resupply_wh_ids': [(6, 0, [self.yourcompany_id.id])]})
                self.wh_op.with_env(newenv).write({
                    'location_id': self.warehouse_id.lot_stock_id.id})
                self.wh_op4.with_env(newenv).write({
                    'location_id': self.warehouse_id4.lot_stock_id.id})
                # Assign location route to product
                stock_lot = self.stock_route.with_env(newenv).search([
                    ('supplied_wh_id', '=', self.warehouse_id.id)], limit=1)
                stock_lot4 = self.stock_route.with_env(newenv).search([
                    ('supplied_wh_id', '=', self.warehouse_id4.id)], limit=1)
                self.product_id.with_env(newenv).write({
                    'route_ids': [(6, 0, stock_lot.ids + stock_lot4.ids)]})
                newenv.cr.commit()
                if procurement_data is not None:
                    sched_id = self.sched.create(procurement_data)
                    sched_id.procure_calculation()
                    for thread in self.get_threads():
                        thread.run()
                    return sched_id.id

    def debug_info(self):
        """ This method is used to print both warehouse, product, procurement
        information when a unit tests fail. This is usefull to
        know the related information about the us identificate
        the reason why fails.
        wh ----->  warehouse
        pc ----->  product
        proc --->  procurement order
        po --->  procurement order
        """
        wh_fields = ['name', 'resupply_wh_ids', 'lot_stock_id',
                     'resupply_from_wh']
        pc_fields = ['name', 'route_ids', 'seller_ids', 'qty_available']
        proc_fields = ['id', 'name', 'location_id', 'warehouse_id', 'rule_id']
        prorule_fields = [
            'id', 'name', 'route_id',
            'procure_method', 'action', 'sequence']
        # compiling debug data for procurement order
        po_all = self.proc.search(
            [('warehouse_id', '=', self.warehouse_id.id)]
        )
        po_return = po_all.read(proc_fields)

        # compiling debug data for product
        pc_all = self.product.search([('id', '=', self.product_id.id)])
        pc_return = pc_all.read(pc_fields)

        # compiling debug data for warehouse
        wh_all = self.warehouse.search(
            [('name', '=', 'Test warehouse 3')])
        wh_return = wh_all.read(wh_fields)

        # compiling debug data for procurement rule
        pr_all = self.procurement_rule.search(
            [('warehouse_id', '=', self.warehouse_id.id)])
        pr_return = pr_all.read(prorule_fields)

        stock_lot_route = self.stock_route.search(
            [('supplied_wh_id', '=', self.warehouse_id.id)])
        stock_lot_route_return = stock_lot_route.read()

        # Formating debug info
        po_data = ('\n\n*** INFO OF ORDERPOINT ***\n\n' +
                   pprint.pformat(po_return) + '\n' +
                   '\n\n*** INFO OF PRODUCT ***\n\n' +
                   pprint.pformat(pc_return) + '\n' +
                   '\n\n*** INFO OF WAREHOUSES ***\n\n' +
                   pprint.pformat(wh_return) + '\n' +
                   '\n\n*** INFO OF PROCURE RULE ***\n\n' +
                   pprint.pformat(pr_return) + '\n' +
                   '\n\n*** STOCK LOCATION ROUTES ***\n\n' +
                   pprint.pformat(stock_lot_route_return))

        return po_data

    # Methods of test
    def test_10_validate_yourcompany_supply_tw3(self):
        """Validate scheduler to testwarehouse 3"""
        dom = [('warehouse_id', '=', self.warehouse_id.id),
               ('product_id', '=', self.product_id.id)]
        self.reset_data(dom)
        self.write_data({'warehouse_id': self.warehouse_id.id})
        proc = self.proc.search(dom, limit=1)
        self.assertEqual(proc.state, 'running', self.debug_info())

    def test_20_validate_importance_supply_tw3(self):
        """Validate the wizard supply only orderpoint like importance selected
        """
        order_point_obj = self.registry('stock.warehouse.orderpoint')
        dom = [('product_id', '=', self.product_id.id),
               ('warehouse_id', '=', self.warehouse_id4.id)]
        self.reset_data(dom)
        self.write_data({'importance': self.importance})
        procurement = self.proc.search(dom, limit=1)
        order_point_srch = order_point_obj.search(self.cr, self.uid, [
            ('product_id', '=', self.product_id.id),
            ('importance', '=', self.importance),
            ('warehouse_id', '=', self.warehouse_id4.id)])
        order_rule = self.order_rule.browse(order_point_srch)
        self.assertEqual(procurement.state, 'running')
        self.assertEqual(order_rule.name, procurement.name)
        self.assertEqual(order_rule.id, procurement.orderpoint_id.id)

    def reset_data(self, domain):
        with openerp.api.Environment.manage():
            with openerp.registry(self.env.cr.dbname).cursor() as newcr:
                newenv = api.Environment(newcr, self.env.uid, self.env.context)
                olds = self.proc.with_env(newenv).search(domain)
                olds.cancel()
                olds.unlink()
                newenv.cr.commit()

    def tearDown(self):
        for thread in self.get_threads():
            thread._Thread__target = True
            thread._Thread__args = True
            thread._Thread__kwargs = True
        super(TestReorderingRule, self).tearDown()
