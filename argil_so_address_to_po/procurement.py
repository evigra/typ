# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@argil.mx)
############################################################################
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

from openerp import netsvc
from openerp.osv import fields, osv
from openerp import _

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        sale_order_obj = self.pool.get('sale.order')
        so_id = sale_order_obj.search(cr, uid, [('name','=',procurement.origin)])
        if so_id:
            for line in sale_order_obj.browse(cr, uid, so_id)[0].order_line:
                if  line.product_id.id == procurement.product_id.id and line.product_uom_qty == procurement.product_qty and \
                    line.product_uom.id == procurement.product_uom.id and line.dropshipping:
                    po_vals.update({'warehouse_id': False, 'dest_address_id':line.order_id.partner_shipping_id.id})                
                
        return super(procurement_order, self).create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context=None)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
