# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields
import time
from datetime import datetime, date
from openerp import _
from openerp import SUPERUSER_ID
from datetime import date, datetime, time, timedelta


class consult_stock_product_wizard(osv.osv_memory):
    _name = 'consult.stock.product.wizard'
    _description = 'Consulta de Existencias'
    _columns = {
    'product_id': fields.many2one('product.product', 'Producto', required=True),
    }
    _defaults = {  

        }
    def consult_stock(self, cr, uid, ids, context=None):
        consult_id = 0
        cr.execute("delete from stock_consult_product;")        
        cr.execute("delete from stock_consult_product_lines;")

        sale_shop = self.pool.get('sale.shop')
        stock_picking = self.pool.get('stock.picking.in')
        stock_move = self.pool.get('stock.move')
        # product_obj = self.pool.get('product.product')
        product_lines = []
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            # product_br = product_obj.browse(cr, SUPERUSER_ID, rec.product_id.id, context=None)
            sale_shop_ids = sale_shop.search(cr, SUPERUSER_ID, [])
            if len(sale_shop_ids) == 1:
                cr.execute("select id from sale_shop;")
                sale_shop_ids = [x[0] for x in cr.fetchall()]

            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
            date_consult = date_strp + timedelta(days=1)
            for shop in sale_shop.browse(cr, SUPERUSER_ID, sale_shop_ids, context=None):
                if shop.warehouse_id:
                    entr = 0.0
                    sal = 0.0
                    vendibles = 0.0
                    location_ids = [shop.warehouse_id.lot_stock_id.id, shop.warehouse_id.lot_input_id.id, shop.warehouse_id.lot_output_id.id]

                    move_in_ids = stock_move.search(cr, uid, [('state','in',('confirmed','assigned')),('product_id','=',rec.product_id.id),('location_dest_id','=',shop.warehouse_id.lot_input_id.id),('picking_id.type','=','in')])
                    move_out_ids = stock_move.search(cr, uid, [('state','in',('confirmed','assigned')),('product_id','=',rec.product_id.id),('location_id','=',shop.warehouse_id.lot_stock_id.id),('picking_id.type','=','out')])
                    if move_in_ids:
                        move_in_ids = tuple(move_in_ids)
                        cr.execute("select sum(product_qty) from stock_move where id in %s", (move_in_ids,))
                        entr = cr.fetchall()
                        if entr[0][0] != None:
                            entr = entr[0][0]
                        else:
                            entr = 0.0
                    if move_out_ids:
                        move_out_ids = tuple(move_out_ids)
                        cr.execute("select sum(product_qty) from stock_move where id in %s", (move_out_ids,))
                        sal = cr.fetchall()
                        if sal[0][0] != None:
                            sal = sal[0][0]
                        else:
                            sal = 0.0
                    stock = self.pool.get('stock.location')._product_get(cr, SUPERUSER_ID, shop.warehouse_id.lot_stock_id.id, [rec.product_id.id], {'uom': rec.product_id.uom_id.id, 'to_date': date_consult, 'compute_child': False})[rec.product_id.id]
                    #entr = self.pool.get('stock.location')._product_get(cr, SUPERUSER_ID, shop.warehouse_id.lot_input_id.id, [rec.product_id.id], {'uom': rec.product_id.uom_id.id, 'to_date': date_consult, 'compute_child': False})[rec.product_id.id]
                    #sal = self.pool.get('stock.location')._product_get(cr, SUPERUSER_ID, shop.warehouse_id.lot_output_id.id, [rec.product_id.id], {'uom': rec.product_id.uom_id.id, 'to_date': date_consult, 'compute_child': False})[rec.product_id.id]
                    virtual = (stock+entr)-sal
                    vendibles = stock - sal
                    xline = (0,0,{
                        'sale_shop': shop.name,
                        'real': stock,
                        'virtual': virtual,
                        'entrantes': entr,
                        'salientes': sal,
                        'vendibles': vendibles,
                        })
                    product_lines.append(xline)
            vals = {
                'product_id': rec.product_id.id,
                # 'date': ,
                'stock_products': [x for x in product_lines],
            }
            consult_id = self.pool.get('stock.consult.product').create(cr, SUPERUSER_ID, vals, context=None)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Existencias'),
            'res_model': 'stock.consult.product',
            'res_id': consult_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'target': 'current',
            'nodestroy': True,
        }
consult_stock_product_wizard()


class stock_consult_product(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'stock.consult.product'
    _description = 'Consulta de Existencias de Productos'
    _rec_name = 'product_id' 
    _columns = {
        'product_id':fields.many2one('product.product', 'Producto', readonly=True),
        'date': fields.date('Fecha', required=True, readonly=True),
        'stock_products': fields.one2many('stock.consult.product.lines','product_id', 'Revision de Existencias', readonly=True),
    }
    _defaults = {  
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        }
stock_consult_product()

class stock_consult_product_lines(osv.osv):
    _name = 'stock.consult.product.lines'
    _description = 'Consulta de Existencias de Productos'
    _rec_name = 'sale_shop' 
    _columns = {
        'product_id':fields.many2one('stock.consult.product', 'ID REF Producto', readonly=True),
        'sale_shop': fields.char('Tienda', size=128),
        'real': fields.float('Existencias', digits=(14,2)),
        'virtual': fields.float('Virtual', digits=(14,2)),
        'entrantes': fields.float('Entrantes', digits=(14,2)),
        'salientes': fields.float('Salientes', digits=(14,2)),
        'vendibles': fields.float('Vendibles', digits=(14,2)),
    }
    _defaults = {  
        }
stock_consult_product_lines()