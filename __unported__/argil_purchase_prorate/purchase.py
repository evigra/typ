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

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
                'prorate_ids': fields.many2many('stock.prorate','purchase_prorate_rel','po_id','sp_id','Purchase Prorates'),
                }


class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns = {
        'prorate_id' : fields.many2one('stock.prorate','Prorate Reference'),
        'local_prorate_id': fields.many2one('stock.prorate','Local Prorate Reference'),
        'loc_inc_price_unit': fields.float('Local Service inc Unit Price', required=False, digits_compute= dp.get_precision('Product Price')),
        'local_currency_id': fields.many2one('res.currency', 'Local Currency'),
    }
    def copy_data(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({'prorate_id':False,'local_prorate_id':False})
        return super(purchase_order_line, self).copy_data(cr, uid, id, default, context)
purchase_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
