# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
import time
from datetime import datetime, date
from openerp import _
from openerp import SUPERUSER_ID
from datetime import date, datetime, time, timedelta
from openerp.tools.translate import _

class consulta_productos_sale_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    _description = 'Consultar Existencias'
    _columns = {
        'consultar': fields.boolean("Consultar Existencias"),
    }
    _defaults = {  
        }
    def consulta_stock(self, cr, uid, ids, product_id, consultar, context=None):
        if not product_id or consultar==False:
        	return {}
        if consultar and product_id:
            sale_shop = self.pool.get('sale.shop')
            stock_picking = self.pool.get('stock.picking.in')
            stock_move = self.pool.get('stock.move')
            product_lines = []
            sale_shop_ids = sale_shop.search(cr, SUPERUSER_ID, [])
            if len(sale_shop_ids) == 1:
                cr.execute("select id from sale_shop;")
                sale_shop_ids = [x[0] for x in cr.fetchall()]
            date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
            date_consult = date_strp + timedelta(days=1)
            mensaje = ""
            for shop in sale_shop.browse(cr, SUPERUSER_ID, sale_shop_ids, context=None):
                if shop.warehouse_id:
                    entr = 0.0
                    sal = 0.0
                    vendibles = 0.0
                    location_ids = [shop.warehouse_id.lot_stock_id.id, shop.warehouse_id.lot_input_id.id, shop.warehouse_id.lot_output_id.id]
                    move_in_ids = stock_move.search(cr, uid, [('state','in',('confirmed','assigned')),('product_id','=',product_id),('location_dest_id','=',shop.warehouse_id.lot_input_id.id),('picking_id.type','=','in')])
                    move_out_ids = stock_move.search(cr, uid, [('state','in',('confirmed','assigned')),('product_id','=',product_id),('location_id','=',shop.warehouse_id.lot_stock_id.id),('picking_id.type','=','out')])
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
                    stock = self.pool.get('stock.location')._product_get(cr, SUPERUSER_ID, shop.warehouse_id.lot_stock_id.id, [product_id], {'to_date': date_consult, 'compute_child': False})[product_id]
                    if len(shop.name)<23:
                    	mensaje += " |||||||||| " + shop.name +" "+" -STOCK- "+ str(int(round(stock)))+ " - " + " |||||||| " + "\n"
            mensaje = mensaje.replace('TIENDA','TYP')
            return {'value': {'consultar': False},'warning': {'title': 'Disponibilidad','message': mensaje}}
consulta_productos_sale_line()