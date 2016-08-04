# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = 'sale.order'
    _columns = {
    'orden_compra': fields.char('Orden de Compra', size=128, help='Honda le Indicara que Numero de Orden de Compra tienen que Capturar'),
    'addenda_honda_partner': fields.boolean('Addenda Honda'),
    'picking_principal_id': fields.many2one('stock.picking.out', 'Picking'),
    }


    _defaults = {

    }
    # commented because there i addenda_honda in res_partner
    # def onchange_partner_id(self, cr, uid, ids, part, context=None):
    #     if not part:
    #         return {'value':{}}
    #     partner = self.pool.get('res.partner').browse(cr, uid, part, context=context)
    #     result =  super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
    #     result['value'].update({'addenda_honda_partner':partner.addenda_honda})
    #     return result

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        res = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None)
        orden_compra = ""
        sale_n = ""
        for order in self.browse(cr, uid, ids, context=context):
            orden_compra = order.orden_compra
            sale_n = order.name
        account_obj = self.pool.get('account.invoice')

        for account in account_obj.browse(cr, uid, [res], context=None):
        	account.write({'orden_compra':orden_compra,'order_id':ids[0]})

        stock_picking = self.pool.get('stock.picking.out')
        picking_ids = stock_picking.search(cr, uid,[('origin','=',sale_n)])
        if picking_ids:
        	self.write(cr, uid, ids, {'picking_principal_id':picking_ids[0]}, context=None)
        return res
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
