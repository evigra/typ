# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

import openerp
from openerp import pooler, tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare

import openerp.addons.decimal_precision as dp
##############################
# stock.warehouse_view
##############################
class stock_warehouse_view(osv.osv):
    _name = 'stock.warehouse_view'
    _description = "Warehouse without Company_id restriction"

    _columns = {
            'name'          : fields.char('Name', size=128),
            'lot_input_id'  : fields.integer('Input Location'),
            'lot_output_id' : fields.integer('Output Location'),
            'lot_stock_id'  : fields.integer('Stock Location'),
            'partner_id'    : fields.integer('Partner'),
            }

    _order = 'name'

stock_warehouse_view()

##############################
# stock.warehouse
##############################
class stock_warehouse(osv.osv):
    _inherit = 'stock.warehouse'

    def create(self, cr, uid, vals, context=None):
        res = super(stock_warehouse, self).create(cr, uid, vals, context)
        sql = """insert into stock_warehouse_view
                        (id, name, lot_input_id, lot_output_id, lot_stock_id, partner_id, create_uid, write_uid, create_date, write_date)
                    values (%s, '%s', %s, %s, %s, %s, %s, %s, '%s', '%s')""" % \
            (res, vals['name'],vals['lot_input_id'], vals['lot_output_id'], vals['lot_stock_id'], vals['partner_id'] or 'NULL',
             uid, uid, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        #print "sql: ", sql
        cr.execute(sql)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(stock_warehouse, self).write(cr, uid, ids, vals, context=context)
        cr.execute("""select id from stock_warehouse_view where id in (%s)""" % ((tuple(ids,))))
        data = cr.fetchall()
        # if not data:
        #     for rec in self.browse(cr,uid, ids):
        #         sql = """insert into stock_warehouse_view
        #                     (id, name, lot_input_id, lot_output_id, lot_stock_id, partner_id, create_uid, write_uid, create_date, write_date)
        #                 values (%s, '%s', %s, %s, %s, %s, %s, %s, '%s', '%s')""" % \
        #             (rec.id, rec.name,rec.lot_input_id.id, rec.lot_output_id.id, rec.lot_stock_id.id, rec.partner_id.id or 'NULL',
        #              uid, uid, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT), time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        # else:
        #     sql = "update stock_warehouse_view set write_uid=%s,write_date='%s'" % (uid, time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        #     datos = {}
        #     #print "vals: ", vals
        #     for val in vals:
        #         if val not in ['name', 'lot_input_id', 'lot_output_id', 'lot_stock_id', 'partner_id']:
        #             continue
        #         #print "val: ", val
        #         sql += (", ") + (" %s = %s" % (val, ("'" + str(vals[val]) + "'") if vals[val] else 'NULL'))
        #     sql += " where id in (%s)"  % ((tuple(ids,)))
        #     #print "sql: ", sql
        # #print sql
        # cr.execute(sql)
        return res


    def unlink(self, cr, uid, ids, context=None):
        res = super(stock_warehouse, self).unlink(cr, uid, ids, context=context)
        sql = """delete from stock_warehouse_view where id in (%s)""" % ((tuple(ids,)))
        cr.execute(sql)
        #print "sql: ", sql
        return res
stock_warehouse()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
