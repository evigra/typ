# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Argil Consulting (<http://www.argil.mx>)
#    Information:
#    Israel Cruz Argil  - israel.cruz@argil.mx
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from openerp import netsvc
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from openerp.tools.float_utils import float_round as round

import openerp.addons.decimal_precision as dp


##############################
# stock.location
##############################
class stock_location(osv.osv):
    _inherit = "stock.location"

    _columns = {
        'valuation_in_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Stock Valuation Account (Incoming)",
            domain="[('type', '=', 'other')]",
            help="Used for real-time inventory valuation. When set on a virtual location (non internal type), this account will be used to hold the value of products being moved from an internal location into this location, instead of the generic Stock Output Account set on the product. This has no effect for internal locations."),
        'valuation_out_account_id': fields.property(
            type='many2one',
            relation='account.account',
            string="Stock Valuation Account (Outgoing)",
            domain="[('type', '=', 'other')]",
            help="Used for real-time inventory valuation. When set on a virtual location (non internal type), this account will be used to hold the value of products being moved out of this location and into an location, instead of the generic Stock Output Account set on the product. This has no effect for internal locations."),
        'transfer_location_type' :  fields.selection([('in','Incoming Transfer'),('out','Outgoing Transfer'),], 'Transfer Type',
                                                     required=False,help="Use this to define locations to be used for Stock Transfers"),

            }

# ##############################
# # stock.warehouse_view
# ##############################
# class stock_warehouse_view(osv.osv):
#     _name = 'stock.warehouse_view'
#     _description = "Warehouse without Company_id restriction"
#
#     _columns = {
#             'name'          : fields.char('Name', size=128),
#             'lot_input_id'  : fields.integer('Input Location'),
#             'lot_output_id' : fields.integer('Output Location'),
#             'lot_stock_id'  : fields.integer('Stock Location'),
#             'partner_id'    : fields.integer('Partner'),
#             }
#
#     _order = 'name'
#
# ##############################
# # stock.warehouse
# ##############################
# class stock_warehouse(osv.osv):
#     _inherit = 'stock.warehouse'
#
#     def create(self, cr, uid, vals, context=None):
#         res = super(stock_warehouse, self).create(cr, uid, vals, context)
#         sql = """insert into stock_warehouse_view
#                         (id, name, lot_input_id, lot_output_id, lot_stock_id, partner_id, create_uid, write_uid, create_date, write_date)
#                     values (%s, '%s', %s, %s, %s, %s, %s, %s, '%s', '%s')""" % \
#             (res, vals['name'],vals['lot_input_id'], vals['lot_output_id'], vals['lot_stock_id'], vals['partner_id'] or 'NULL',
#              uid, uid, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
#         #print "sql: ", sql
#         cr.execute(sql)
#         return res
#
#     def write(self, cr, uid, ids, vals, context=None):
#         res = super(stock_warehouse, self).write(cr, uid, ids, vals, context=context)
#         cr.execute("""select id from stock_warehouse_view where id in (%s)""" % ((tuple(ids,))))
#         data = cr.fetchall()
#         if not data:
#             for rec in self.browse(cr,uid, ids):
#                 sql = """insert into stock_warehouse_view
#                             (id, name, lot_input_id, lot_output_id, lot_stock_id, partner_id, create_uid, write_uid, create_date, write_date)
#                         values (%s, '%s', %s, %s, %s, %s, %s, %s, '%s', '%s')""" % \
#                     (rec.id, rec.name,rec.lot_input_id.id, rec.lot_output_id.id, rec.lot_stock_id.id, rec.partner_id.id or 'NULL',
#                      uid, uid, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
#         else:
#             sql = "update stock_warehouse_view set write_uid=%s,write_date'%s'" % (uid, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
#             datos = {}
#             #print "vals: ", vals
#             for val in vals:
#                 #print "val: ", val
#                 sql += (", ") + (" %s = %s" % (val, ("'" + str(vals[val]) + "'") if vals[val] else 'NULL'))
#             sql += " where id in (%s)"  % ((tuple(ids,)))
#             #print "sql: ", sql
#         cr.execute(sql)
#         return res
#
#
#     def unlink(self, cr, uid, ids, context=None):
#         res = super(stock_warehouse, self).unlink(cr, uid, ids, context=context)
#         sql = """delete from stock_warehouse_view where id in (%s)""" % ((tuple(ids,)))
#         cr.execute(sql)
#         #print "sql: ", sql
#         return res



##############################
# stock.move
##############################
class stock_move(osv.osv):
    _inherit = 'stock.move'


    _columns = {
        'stock_transfer_line_id' : fields.one2many('stock.transfer.line', 'stock_move_id', 'Stock Transfer Line', readonly=True),
        'stock_transfer_id'  : fields.related('stock_transfer_line_id', 'transfer_id', type='many2one', relation='stock.transfer', string='Stock Transfer', store=True, readonly=True),
            }
    # Se pondra a ceros los cargos y abonos para los movimientos cuya Ubicacion sea:
    # - Origen: Tipo Inventario = Destino: Tipo Inventario
    # - Origen: Tipo Transferencia = Destino: Tipo Transferencia
    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        res_prev = super(stock_move, self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None)
        res = res_prev
        #print "res before: \n", res
        if move.location_id.usage in ('inventory','transit') and move.location_dest_id.usage in ('inventory','transit') and \
            move.location_id.transfer_location and move.location_dest_id.transfer_location:
            return []
            res[0][2].update({'debit': 0.0, 'credit': 0.0})
            res[1][2].update({'debit': 0.0, 'credit': 0.0})
        #print "res: after \n", res
        return res


##############################
# purchase.order
##############################
class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def _info_for_transfers(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        transfer_expense_obj = self.pool.get('stock.transfer.expense')
        for order in self.browse(cr, uid, ids, context=context):
            flag = True
            for line in order.order_line:
                if line.product_id and line.product_id.type != 'service':
                    flag = False
            transfer_expense_ids = transfer_expense_obj.search(cr, uid, [('purchase_order_id','=',order.id)])
            used_amount = 0.0
            for transfer_expense in transfer_expense_obj.browse(cr, uid, transfer_expense_ids):
                used_amount += transfer_expense.amount
            res[order.id] = {'usable_for_transfer' : (order.amount_untaxed > used_amount) and flag,
                             'usable_amount_for_transfer' : (order.amount_untaxed - used_amount) if flag else 0.0,
                             }
        return res

    def _get_transfer(self, cr, uid, ids, context=None):
        result = {}
        for expense_line in self.pool.get('stock.transfer.expense').browse(cr, uid, ids, context=context):
            result[expense_line.purchase_order_id.id] = True
        return result.keys()


    _columns = {
        'usable_for_transfer'   : fields.function(_info_for_transfers, string='Usable for Transfer', type='boolean', method=True,
                                store={ 'purchase.order': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                        'stock.transfer.expense': (_get_transfer, ['purchase_order_id'], 20),

                                        }, multi=True),
        'usable_amount_for_transfer': fields.function(_info_for_transfers, string='Usable Amount for Transfer', type='float', method=True,
                                store={ 'purchase.order': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                        'stock.transfer.expense': (_get_transfer, ['purchase_order_id'], 20),
                                        }, multi=True, digits_compute= dp.get_precision('Sale Price')),
        'transfer_expense_line_ids'  : fields.one2many('stock.transfer.expense', 'purchase_order_id', 'Related Transfer', readonly=True),

            }

##############################
# stock.transfer
##############################
class stock_transfer(osv.osv):
    _name = "stock.transfer"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Stock Transfer between Warehouses"


    def _sum_product_cost(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res1 = res2 = 0.0
            for line in rec.transfer_line:
                res1 += line.amount_product_cost
                res2 += line.amount
            res[rec.id] = {'product_cost_wo_expenses' : res1,
                           'product_cost_amount'      : res2,
                            }
        return res

    def _sum_expenses(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result = 0.0
            for line in rec.expense_line:
                result += line.amount
            res[rec.id] = result
        return res

    _columns = {
        'state'         : fields.selection([('draft','Draft'), ('done','Done'), ('cancel','Cancelled')], 'Status', readonly=True),
        'name'          : fields.char('Name', size=64, required=True),
        'origin'        : fields.char('Origin', size=64, readonly=True),
        'type'          : fields.selection([
                                            ('in','Transfer In'),
                                            ('out','Transfer Out'),
                                        ], 'Type', required=True),

        'date'          : fields.date('Date', required=True, readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'eta'           : fields.datetime('E.T.A.', readonly=True, select=True, states={'draft': [('readonly', False)]}),
        'warehouse_id'  : fields.many2one('stock.warehouse', 'Warehouse', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'location_id'   : fields.many2one('stock.location', 'Location', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'warehouse_subsidiary_id' : fields.many2one('stock.warehouse_view', 'Warehouse Subsidiary', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'notes'         : fields.text('Notes', readonly=True, states={'draft': [('readonly', False)]}),
        'transfer_line' : fields.one2many('stock.transfer.line', 'transfer_id', 'Stock Transfer Lines', readonly=True, states={'draft': [('readonly', False)]}),
        'product_cost_wo_expenses'  : fields.function(_sum_product_cost, string="Product Cost With No Expenses",
                                                      type='float', digits_compute=dp.get_precision('Account'),
                                                      store=False, multi=True),
        'product_cost_amount'       : fields.function(_sum_product_cost, string="Product Cost With Expenses",
                                                      type='float', digits_compute=dp.get_precision('Account'),
                                                      store=False, multi=True),

        'expense_line'  : fields.one2many('stock.transfer.expense', 'transfer_id', 'Related Expenses', readonly=True, states={'draft': [('readonly', False)]}),
        'expense_amount': fields.function(_sum_expenses, string="Expenses Amount", type='float', digits_compute=dp.get_precision('Account'), store=False, multi=False),
        'dummy'         : fields.boolean('Dummy'),
        'transfer_id_to_receive': fields.integer('Transfer Destiny ID', readonly=True),
        #'transfer_origin_ids': fields.one2many('stock.transfer', 'transfer_id_to_receive', 'Transfer From', readonly=True),        'expense_account_move_id'  : fields.many2one('account.move', 'Account Move', required=False, readonly=True),
        'company_id'    : fields.many2one('res.company', 'Company'),
        'expense_account_move_id' : fields.many2one('account.move', 'Account Move'),
        'received'      : fields.boolean('Received', readonly=True,),
    }

    _defaults = {
        'name' : lambda *a : '/',
        'state': lambda *a : 'draft',
        'date' : lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'eta'  : lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
        'transfer_id_to_receive' : lambda *a : 0,
    }

    #_sql_constraints = [
    #    ('name_uniq', 'unique(name,company_id)', 'Transfer ID must be unique per company!'),
    #    ]


    _order = "date desc, name desc"


    def on_change_warehouse_id(self, cr, uid, ids, warehouse_id, context=None):
        context = context or {}
        if not warehouse_id:
            return {'value': {'location_id': False}}
        return {'value': {'location_id': self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id).lot_stock_id.id}}

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/' and vals['type'] == 'out':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.transfer.' +  vals['type'] )  or '/'
        return super(stock_transfer, self).create(cr, uid, vals, context=context)

    def action_assign_expenses(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('stock.transfer.line')
        for rec in self.browse(cr, uid, ids):
            stock_value = rec.product_cost_wo_expenses
            expenses = rec.expense_amount
            for line in rec.transfer_line:
                line_obj.write(cr, uid, line.id, {'amount_expenses' : (expenses * (line.amount_product_cost / stock_value)) if (stock_value and expenses) else 0.0})
        return True

    def button_dummy(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'dummy':1})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        #print "vals: ", vals
        #print "ids: ", ids
        for rec in self.browse(cr, uid, ids):
            if rec.name == '/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'stock.transfer.' +  rec.type )  or '/'
        res = super(stock_transfer, self).write(cr, uid, ids, vals, context=context)
        if not('state' in vals and vals['state'] in ('cancel', 'done')):
            self.action_assign_expenses(cr, uid, ids)
        return res

    def action_cancel(self, cr, uid, ids, context=None):
        message_obj = self.pool.get('mail.message')
        stock_move_obj = self.pool.get('stock.move')
        username = self.pool.get('res.users').read(cr, uid, [uid], ['name'])[0]['name']
        for rec in self.browse(cr, uid, ids):
            if rec.type=='in':
                raise osv.except_osv(
                            _('Warning !'),
                            _('You can not Cancel Incoming Transfer, you should call Departure Subsidiary to ask them to Cancel this record.'))
            elif rec.state == 'draft':
                message = {
                    'type': 'notification',
                    'model': 'stock.transfer',
                    'res_id': rec.id,
                    'record_name' : _('Stock Transfer %s') % (rec.name),
                    'body': '<div><span>' + (_('Stock Transfer has been Cancelled by %s') % (username)) + '</span></div>',
                        }
                self.write(cr, uid, ids, {'state':'cancel'})
            elif rec.state == 'done' and not rec.received:
                stock_transfer_line_obj = self.pool.get('stock.transfer.line')
                stock_location_obj = self.pool.get('stock.location')
                location_id = stock_location_obj.search(cr, uid, [('usage','in',('inventory','transit')),('transfer_location_type','=','in'),
                                                                  '|',('company_id','=',rec.company_id.id),('company_id','=',False)])
                if not location_id:
                    raise osv.except_osv(_('Error!'),_('You have no Stock Location defined for Incoming Stock Transfer'))
                todo=[]
                for line in rec.transfer_line:
                    todo.append(line.id)
                if not stock_transfer_line_obj.action_return(cr, uid, todo, location_id[0], context=context):
                    raise osv.except_osv(_('Warning!'),_('There was a problem creating Stock Moves for returning products, please check...'))

                if rec.expense_account_move_id and rec.expense_account_move_id.id:
                    account_move_obj = self.pool.get('account.move')
                    if rec.expense_account_move_id.state=='posted':
                        account_move_obj.button_cancel(cr, uid, [rec.expense_account_move_id.id])
                    account_move_obj.unlink(cr, uid, [rec.expense_account_move_id.id])

                cr.execute('select id, state, name from stock_transfer where id=%s;' % (rec.transfer_id_to_receive))
                data = cr.fetchall()
                #print "======================="
                #print "data: ", data
                #print "======================="
                if data:
                    if data[0][1] == 'draft':
                        message = {
                            'type': 'notification',
                            'model': 'stock.transfer',
                            'res_id': data[0][0],
                            'record_name' : _('Stock Transfer %s') % (data[0][2]),
                            'body': '<div><span>' + (_('Stock Transfer has been Cancelled by Departure Subsidiary by %s') % (username)) + '</span></div>',
                                }
                        res_message = message_obj.create(cr, uid, message)
                        cr.execute("""update stock_transfer set state='cancel' where id=%s;""" % (rec.transfer_id_to_receive))
                    elif rec.received:
                        raise osv.except_osv(
                            _('Warning !'),
                            _('You can not Cancel Outgoing Transfer when is already received by subsidiary.'))

                message = {
                        'type': 'notification',
                        'model': 'stock.transfer',
                        'res_id': rec.id,
                        'record_name' : _('Stock Transfer %s') % (rec.name),
                        'body': '<div><span>' + (_('Stock Transfer has been Cancelled by %s') % (username)) + '</span></div>',
                            }
            res_message = message_obj.create(cr, uid, message)
            self.write(cr, uid, [rec.id], {'state':'cancel'})
            if rec.expense_line:
                self.pool.get('stock.transfer.expense').unlink(cr, uid, [x.id for x in rec.expense_line])
            if rec.transfer_line:
                self.pool.get('stock.transfer.line').unlink(cr, uid, [x.id for x in rec.transfer_line])

        return True

    def action_confirm_transfer(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        stock_transfer_line_obj = self.pool.get('stock.transfer.line')
        account_move_obj = self.pool.get('account.move')
        stock_location_obj = self.pool.get('stock.location')
        account_fiscal_obj=self.pool.get('account.fiscal.position')
        todo = []
        for rec in self.browse(cr, uid, ids, context=context):
            if not rec.transfer_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a Stock Transfer without any product line.'))
            for line in rec.transfer_line:
                todo.append(line.id)

            transfer_type = rec.type
            location_id = stock_location_obj.search(cr, uid, [('usage','in',('inventory','transit')),
                                                              ('transfer_location_type','=',transfer_type),
                                                              '|',('company_id','=',rec.company_id.id),('company_id','=',False)])
            if not location_id:
                raise osv.except_osv(_('Error!'),_('You have no Stock Location defined for %s Stock Transfer') % (_('Outgoing') if transfer_type == 'out' else _('Incoming')))
            location = stock_location_obj.browse(cr, uid, location_id)
            location_account = location[0].valuation_in_account_id.id if transfer_type=='out' \
                        else location[0].valuation_out_account_id.id

            if not location_account:
                raise osv.except_osv(_('Error!'),_('You have no Account defined for Stock Location %s') % (location[0].name))
            #print "todo: ", todo
            if not stock_transfer_line_obj.action_confirm(cr, uid, todo, transfer_type, location_id[0], context=context):
                raise osv.except_osv(_('Warning!'),_('There was a problem creating Stock Moves, please check...'))

            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
            period_id = account_move_obj._get_period(cr, uid,context=context)

            move_lines = []
            for expense in rec.expense_line:
                for po_line in expense.purchase_order_id.order_line:
                    prod_account = po_line.product_id.property_account_expense.id or po_line.product_id.categ_id.property_account_expense_categ.id or False
                    if not prod_account:
                        raise osv.except_osv(_('Warning !'),
                            _('Expense Account is not defined for product %s (id:%d)') % \
                                (po_line.product_id.name, po_line.product_id.id,))
                    move_line = (0,0, {
                        'name'              : _('Reclassification of expenditure: ') + expense.purchase_order_id.name + ' - ' + po_line.name,
                        'ref'               : expense.purchase_order_id.name + ' - ' + po_line.name,
                        'product_id'        : po_line.product_id.id,
                        'product_uom_id'    : po_line.product_uom.id,
                        'account_id'        : account_fiscal_obj.map_account(cr, uid, False, prod_account),
                        'debit'             : 0.0,
                        'credit'            : round((po_line.price_subtotal / po_line.order_id.amount_untaxed) * expense.amount, precision),
                        'quantity'          : po_line.product_qty,
                        'journal_id'        : line.product_id.categ_id.property_stock_journal.id,
                        'period_id'         : period_id,
                        })
                    move_lines.append(move_line)

            if move_lines:
                move_line = (0,0, {
                        'name'              : _('Reclassification of expenditure: ') + expense.purchase_order_id.name + ' - ' + po_line.name,
                        'ref'               : rec.name,
                        'account_id'        : account_fiscal_obj.map_account(cr, uid, False, location_account),
                        'debit'             : round(rec.expense_amount, precision),
                        'credit'            : 0.0,
                        'journal_id'        : line.product_id.categ_id.property_stock_journal.id,
                        'period_id'         : period_id,
                        })
                move_lines.append(move_line)
                account_move = {
                        'period_id'     : period_id,
                        'date'          : context.get('date', fields.date.context_today(self,cr,uid,context=context)),
                        'journal_id'    : line.product_id.categ_id.property_stock_journal.id,
                        'line_id'       : move_lines,
                        'ref'           : rec.name,
                        }
                move_id = account_move_obj.create(cr, uid, account_move, context=context)
                self.write(cr, uid, [rec.id], {'expense_account_move_id': move_id})

            # Crear Transferencia de Entrada
            if transfer_type == 'out':
                self.create_transfer_to_receive(cr, uid, rec, context)
            else:
                cr.execute("update stock_transfer set received=true where transfer_id_to_receive=%s;" % (rec.id))
                #raise osv.except_osv('Warning !','Pausa')

        username = self.pool.get('res.users').read(cr, uid, [uid], ['name'])[0]['name']
        for id in ids:
            message_obj = self.pool.get('mail.message')
            message = {
                    'type': 'notification',
                    'model': 'stock.transfer',
                    'res_id': id,
                    'record_name' : _('Stock Transfer %s') % (rec.name),
                    'body': '<div><span>' + (_('Stock Transfer has been Done by %s') % (username)) + '</span></div>',
                        }
            res_message = message_obj.create(cr, uid, message)
            self.write(cr, uid, [id], {'state' : 'done'})
        return True

    def get_receive_line_data(self, cr, uid, transfer, line, context=None):
        result = {
                    'product_id'     : line.product_id.id,
                    'product_uom'    : line.product_uom.id,
                    'qty'            : line.qty,
                    'standard_price' : line.amount_per_uom,
                    'standard_e_dummy' : line.amount_per_uom,
                    'origin_transfer_line_id' : line.id,
                    'origin_qty'     : line.qty,
                        }
        return result

    def create_transfer_to_receive(self, cr, uid, transfer, context=None):
        _transfer_lines = []
        for line in transfer.transfer_line:
            _line = (0, 0, self.get_receive_line_data(cr, uid, transfer, line, context))
            _transfer_lines.append(_line)

        _transfer = {
                    'name' : '/',
                    'origin' : transfer.name,
                    'type' : 'in',
                    'date' : transfer.date,
                    'eta'  : transfer.eta,
                    'warehouse_id'  : transfer.warehouse_subsidiary_id.id,
                    'location_id'   : transfer.warehouse_subsidiary_id.lot_stock_id,
                    'warehouse_subsidiary_id' : transfer.warehouse_id.id,
                    'notes': transfer.notes,
                    'transfer_line' : _transfer_lines,
                }
        #print "======================="
        #print "_transfer: ", _transfer
        #print "======================="
        res = self.create(cr, uid, _transfer)
        cr.execute("update stock_transfer set company_id = (select company_id from stock_warehouse where id = %s) where id = %s" % (transfer.warehouse_subsidiary_id.id, res))
        self.write(cr, uid, [transfer.id], {'transfer_id_to_receive' : res})
        return res


    def is_transfer_done(self, cr, uid, ids, *args):
        for transfer in self.browse(cr, uid, ids):
            return transfer.received
        return False

##############################
# stock.transfer.line
##############################
class stock_transfer_line(osv.osv):
    _name = "stock.transfer.line"
    _description = "Stock Transfer Line"

    def _total_cost(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            res[rec.id] =  {'amount_product_cost': rec.qty * rec.standard_price,
                            'amount' : rec.qty * rec.standard_price + (rec.amount_expenses or 0.0),
                            'amount_per_uom' : rec.qty and ((rec.qty * rec.standard_price + (rec.amount_expenses or 0.0)) / rec.qty) or 0.0,
                            }
        return res

    _columns = {
        'transfer_id'    : fields.many2one('stock.transfer', 'Transfer', required=True),
        'product_id'     : fields.many2one('product.product', 'Product', required=True),
        'product_uom'    : fields.many2one('product.uom', 'UoM', required=True),
        'qty'            : fields.float('Qty', required=True, digits_compute=dp.get_precision('Product Unit of Measure')),
        'standard_price' : fields.float('Price', required=True, digits_compute=dp.get_precision('Account')),
        'standard_price_dummy' : fields.float('Price', required=True, digits_compute=dp.get_precision('Account')),
        'amount_product_cost'    : fields.function(_total_cost, string='Amount', method=True, multi=True, type='float', store=True, digits_compute=dp.get_precision('Account')),
        'amount_expenses': fields.float('Expenses', digits_compute=dp.get_precision('Account'), readonly=True),
        'amount'         : fields.function(_total_cost, string='Total', method=True, multi=True, type='float', store=True, digits_compute=dp.get_precision('Account')),
        'amount_per_uom' : fields.function(_total_cost, string='Cost per UoM', method=True, multi=True, type='float', store=True, digits_compute=dp.get_precision('Account')),
        'amount_percent': fields.float('Amount Percent', digits_compute=dp.get_precision('Account'), readonly=True),
        'stock_move_id'  : fields.many2one('stock.move', 'Stock Move', required=False),
        'stock_move_return_id'  : fields.many2one('stock.move', 'Stock Move Return', required=False),
        'origin_transfer_line_id' : fields.integer('Origin Transfer ID'),
        'origin_qty'     : fields.float('Original Qty', digits_compute=dp.get_precision('Product Unit of Measure')),
        }

    _defaults = {
        'qty':1.0,
    }
    def create(self, cr, uid, vals, context=None):
        vals['standard_price_dummy'] = vals['standard_price']
        if 'amount_expenses' not in vals:
            vals['amount_expenses'] = 0.0
        return super(stock_transfer_line, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'standard_price_dummy' in vals or 'standard_price' in vals:
            #print "vals: ", vals
            vals['standard_price_dummy'] = vals['standard_price'] if 'standard_price' in vals else self.browse(cr, uid, ids)[0].standard_price
        return super(stock_transfer_line, self).write(cr, uid, ids, vals, context=context)

    def on_change_product_id(self, cr, uid, ids, product_id, context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        if not product_id:
            return {'value': {'qty' : 0.0,
                              'product_uom': False,
                              'standard_price': 0.0,
                              'standard_price_dummy': 0.0,}
                    }

        product = product_obj.browse(cr, uid, product_id, context=context)
        result = {'value': {
                            #'qty' : 0.0,
                          'product_uom': product.uom_id.id,
                          'standard_price': product.standard_price,
                          'standard_price_dummy': product.standard_price,}
                }
        #print "result: ", result
        return result

    def on_change_product_uom(self, cr, uid, ids, product_id, product_uom, qty, standard_price, context=None):
        context = context or {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')
        result = {}
        warning = {}
        warning_msgs = ''
        if product_id:
            product = product_obj.browse(cr, uid, product_id)
        if not product_uom:
            result = {	'qty' : 0.0,
             			'product_uom': product.uom_id.id,
              			'standard_price': product.standard_price,
                        'standard_price_dummy': product.standard_price,
                        }
        else:
            uom = product_uom_obj.browse(cr, uid, product_uom)
            if uom.category_id.id != product.uom_id.category_id.id:
                warning_msgs = _('You can not use UoM %s because it is not in the same UoM Category for this Product') % (uom.name)
                result = {'product_uom': product.uom_id.id,}
            elif uom.id != product.uom_id.id:
                factor = product.uom_id.factor * uom.factor
                #print "factor: ", factor
                #print "standard_price * factor = ", standard_price / factor
                result = {'standard_price': product.standard_price / factor, 'standard_price_dummy': product.standard_price / factor,}

        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': {}, 'warning': warning}

    def on_change_qty(self, cr, uid, ids, qty, standard_price, context=None):
        context = context or {}
        return {'value': {'amount_product_cost' : qty * standard_price}
                }



    def create_stock_move(self, cr, uid, line, stock_move_obj, transfer_type, location_id, company_id, context=None):
        if not line:
            return False
        if context is None:
            context = {}
        xmove = {
            'name'              : line.product_id.name or '',
            'product_id'        : line.product_id.id,
            'product_qty'       : line.qty,
            'product_uos_qty'   : line.qty,
            'product_uom'       : line.product_uom.id,
            'product_uos'       : line.product_uom.id,
            'date'              : context.get('date', fields.date.context_today(self,cr,uid,context=context)),
            'date_expected'     : context.get('date', fields.date.context_today(self,cr,uid,context=context)),
            'location_id'       : line.transfer_id.location_id.id if transfer_type =='out' else location_id,
            'location_dest_id'  : line.transfer_id.location_id.id if transfer_type =='in' else location_id,
            'origin'            : line.transfer_id.name,
            #'partner_id'        : line.transfer_id.warehouse_subsidiary_id.partner_id or False,
            'state'             : 'draft',
            'type'              : transfer_type,
            'company_id'        : company_id,
            'price_unit'        : line.product_id.standard_price if transfer_type=='out' else (line.amount / line.qty),
            'auto_validate'     : True,
            }
        #print "======================="
        #print "xmove: ", xmove
        #print "======================="
        return xmove

    def action_confirm(self, cr, uid, ids, transfer_type, location_id, context=None):
        if context is None:
            context = {}
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        stock_move_obj = self.pool.get('stock.move')
        todo_moves = []
        moves_done = []
        for line in self.browse(cr, uid, ids):
            stock_move = stock_move_obj.create(cr, uid, self.create_stock_move(cr, uid, line,
                                                stock_move_obj, transfer_type, location_id, company_id, context))
            if stock_move:
                todo_moves.append(stock_move)
                moves_done.append((line.id, stock_move))
        if todo_moves:
            picking_obj = self.pool.get('stock.picking')
            picking = {
                    'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.' + line.transfer_id.type),
                    'origin': line.transfer_id.name,
                    'type': line.transfer_id.type,
                    'note': line.transfer_id.notes or '',
                    'move_type': 'one',
                    'auto_picking': False,
                    #'stock_journal_id': moves_todo[0][1][3],
                    'company_id': company_id,
                    #'partner_id': line.transfer_id.warehouse_subsidiary_id.partner_id or False,
                    'invoice_state': 'none',
                    'date': context.get('date', fields.date.context_today(self,cr,uid,context=context)),
                }
            picking_id = picking_obj.create(cr, uid, picking)
            stock_move_obj.write(cr, uid, todo_moves, {'picking_id': picking_id})
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

            #stock_move_obj.action_confirm(cr, uid, todo_moves)
            #stock_move_obj.force_assign(cr, uid, todo_moves)
            partial_data = {'delivery_date' : context.get('date', fields.date.context_today(self,cr,uid,context=context))}
            for _move in stock_move_obj.browse(cr, uid, todo_moves):
                partial_data['move%s' % (_move.id)] = {
                                                    'product_id'    : _move.product_id.id,
                                                    'product_qty'   : _move.product_qty,
                                                    'product_uom'   : _move.product_uom.id,
                                                    'prodlot_id'    : _move.prodlot_id.id,
                                                    'product_price' : _move.price_unit,
                                                    'product_currency' : _move.price_currency_id.id,
                                                    }
            stock_move_obj.do_partial(cr, uid, todo_moves, partial_data)
            #stock_move_obj.action_done(cr, uid, todo_moves)
            #print "moves_done: ", moves_done
            for (x,y) in moves_done:
                self.write(cr, uid, x, {'stock_move_id':y})
        return True

    def create_stock_move_return(self, cr, uid, move, stock_move_obj, location_id, context=None):
        if not move:
            return False
        if context is None:
            context = {}
        xmove = {
            'name'              : move.product_id.name or '',
            'product_id'        : move.product_id.id,
            'product_qty'       : move.product_qty,
            'product_uos_qty'   : move.product_uos_qty,
            'product_uom'       : move.product_uom.id,
            'product_uos'       : move.product_uos.id,
            'date'              : context.get('date', fields.date.context_today(self,cr,uid,context=context)),
            'date_expected'     : context.get('date', fields.date.context_today(self,cr,uid,context=context)),
            'location_id'       : location_id,
            'location_dest_id'  : move.location_id.id,
            'origin'            : move.stock_transfer_id.name,
            #'partner_id'        : line.transfer_id.warehouse_subsidiary_id.partner_id or False,
            'state'             : 'draft',
            'type'              : 'in',
            'company_id'        : move.company_id.id,
            'price_unit'        : move.price_unit,
            'auto_validate'     : True,
            }
        #print "======================="
        #print "xmove: ", xmove
        #print "======================="
        return stock_move_obj.create(cr, uid, xmove)



    def action_return(self, cr, uid, ids, location_id, context=None):
        if context is None:
            context = {}
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        stock_move_obj = self.pool.get('stock.move')
        todo_moves = []
        moves_done = []
        for line in self.browse(cr, uid, ids):
            stock_move = self.create_stock_move_return(cr, uid, line.stock_move_id, stock_move_obj, location_id, context)
            if stock_move:
                todo_moves.append(stock_move)
                moves_done.append((line.id, stock_move))
        if todo_moves:
            picking_obj = self.pool.get('stock.picking')
            picking = {
                    'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
                    'origin': line.transfer_id.name,
                    'type': line.transfer_id.type,
                    'note': line.transfer_id.notes or '',
                    'move_type': 'one',
                    'auto_picking': False,
                    #'stock_journal_id': moves_todo[0][1][3],
                    'company_id': company_id,
                    #'partner_id': line.transfer_id.warehouse_subsidiary_id.partner_id or False,
                    'invoice_state': 'none',
                    'date': context.get('date', fields.date.context_today(self,cr,uid,context=context)),
                }
            picking_id = picking_obj.create(cr, uid, picking)
            stock_move_obj.write(cr, uid, todo_moves, {'picking_id': picking_id})
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

            partial_data = {'delivery_date' : context.get('date', fields.date.context_today(self,cr,uid,context=context))}
            for _move in stock_move_obj.browse(cr, uid, todo_moves):
                partial_data['move%s' % (_move.id)] = {
                                                    'product_id'    : _move.product_id.id,
                                                    'product_qty'   : _move.product_qty,
                                                    'product_uom'   : _move.product_uom.id,
                                                    'prodlot_id'    : _move.prodlot_id.id,
                                                    'product_price' : _move.price_unit,
                                                    'product_currency' : _move.price_currency_id.id,
                                                    }
            stock_move_obj.do_partial(cr, uid, todo_moves, partial_data)

            for (x,y) in moves_done:
                self.write(cr, uid, x, {'stock_move_return_id':y})
        return True
##############################
# stock.transfer.expense
##############################
class stock_transfer_expense(osv.osv):
    _name = "stock.transfer.expense"
    _description = "Stock Transfer Expenses"

    def _get_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            #print "rec.purchase_order_id.id: ", rec.purchase_order_id.id
            purchase_amount = self.pool.get('purchase.order').browse(cr, uid, rec.purchase_order_id.id).amount_untaxed
            #print "purchase_amount: ", purchase_amount
            if rec.assigned_percent:
                #print "Percent"
                #print "rec.assigned_percent: ", rec.assigned_percent
                amount = purchase_amount * rec.assigned_percent / 100.00
            else:
                #print "Fixed"
                amount = rec.assigned_amount if rec.assigned_amount <= purchase_amount else purchase_amount
            #print "amount: ", amount
            res[rec.id] = amount
        return res


    _columns = {
        'transfer_id'           : fields.many2one('stock.transfer', 'Transfer', required=True),
        'purchase_order_id'     : fields.many2one('purchase.order', 'Purchase Order', required=True, domain=[('state','in',('approved','done'))]),
        'purchase_order_amount' : fields.related('purchase_order_id', 'amount_untaxed', string='Purchase Subtotal', type='float', store=True, readonly=True, digits_compute=dp.get_precision('Account')),
        'assigned_percent'      : fields.float('Percent (%)', required=True, digits_compute=dp.get_precision('Account')),
        'assigned_amount'       : fields.float('Fixed Amount', required=True, digits_compute=dp.get_precision('Account')),
        'amount'                : fields.function(_get_amount, string='Amount', method=True, store=True, multi=False, digits_compute=dp.get_precision('Account')),
        'notes'                 : fields.text('Notes'),
        }

    _rec_name='purchase_order_id'

    _sql_constraints = [
        ('transfer_id_po_uniq', 'unique(transfer_id,purchase_order_id)', 'Purchase Order cannot be added more than once in the record!'),
        ]


    def _check_available_amount(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids):
            precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Sale Price')
            return (round(rec.purchase_order_id.usable_amount_for_transfer, precision) >= \
                    round((rec.purchase_order_id.amount_untaxed * rec.assigned_percent / 100.0) if rec.assigned_percent else rec.assigned_amount, precision)
                    )
        return False

    _constraints = [
        (_check_available_amount, 'Error ! You can not assign Expense amount greater than available.', ['amount'])
    ]


    def on_change_purchase_order_id(self, cr, uid, ids, purchase_order_id, context=None):
        context = context or {}
        result = {}
        po_obj = self.pool.get('purchase.order')
        if purchase_order_id:
            po = po_obj.browse(cr, uid, purchase_order_id)
            result =  {'value': {'purchase_order_amount' : po.amount_untaxed or 0.0,
                                 'assigned_amount': po.usable_amount_for_transfer,
                                 }
                       }
        #print "result: ", result
        return result


    def on_change_assigned_percent(self, cr, uid, ids, assigned_percent, context=None):
        context = context or {}
        result = {}
        if assigned_percent:
            result = {'value': {'assigned_amount' : 0.0,}}
        if assigned_percent > 100:
            result['value']['assigned_percent'] = 100.0
        #print "result: ", result
        return result

    def on_change_assigned_amount(self, cr, uid, ids, assigned_amount, purchase_order_id, context=None):
        context = context or {}
        result = {}
        if assigned_amount:
            result = {'value': {'assigned_percent' : 0.0, }}
        purchase_subtotal = 0.0
        if purchase_order_id:
            purchase_subtotal = self.pool.get('purchase.order').browse(cr, uid, purchase_order_id).amount_untaxed or 0.0
        if assigned_amount > purchase_subtotal:
            result['value']['assigned_amount'] = purchase_subtotal

        #print "result: ", result
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

