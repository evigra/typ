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

class sale_order(osv.osv):
    _inherit = "sale.order"
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        result = super(sale_order, self)._prepare_order_line_procurement(cr, uid, order, line, move_id, date_planned, context=context)
        result.update({'distribution_type':'sale'})
        return result
        
sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'type': fields.selection([('make_to_stock','From Stock'),
                                  ('make_to_order','On Order'),
                                  ('make_to_supply_request','On Supply Request')],
                                 'Procurement Method', required=True, readonly=True, 
                                 states={'draft': [('readonly', False)]},
                                 help="From stock: When needed, the product is taken from the "\
                                 "stock or we wait for replenishment.\nOn order: When needed, the "\
                                 "product is purchased or produced.\nOn Supply Request: When needed, "\
                                 "a request to distribution center is created"),
    }
sale_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
