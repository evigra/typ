# -*- encoding: utf-8 -*-

#### 
from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID

#### HERENCIA DE PEDIDOS DE VENTA
class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit ='sale.order'
    _columns = {
        }

    _defaults = {
        }

    def force_closing(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.state == 'progress':
                stock_obj = self.pool.get('stock.picking.out')
                stock_id = stock_obj.search(cr, uid,
                    [('origin','=',rec.name)])
                stock_send = False
                for picking in stock_obj.browse(cr, uid, stock_id,
                                            context=context):
                    if picking.state == 'done':
                        stock_send = True
                    else:
                        stock_send = False
                invoice_obj = self.pool.get('account.invoice')
                invoice_id = invoice_obj.search(cr, uid, 
                    [('origin','like',rec.name)])
                invoice_done = False
                for invoice in invoice_obj.browse(cr, uid,
                    invoice_id, context=None):
                    if invoice.state == 'paid':
                        invoice_done = True
                    else:
                        invoice_done = False
                if stock_send == True and invoice_done == True:
                    rec.action_done()
        return True