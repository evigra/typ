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

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    def _get_price_unit_invoice(self, cursor, user, move_line, type):
        if move_line.purchase_line_id and move_line.prorate_id:
            return move_line.purchase_line_id.price_unit
        return super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)
stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
        'prorate_id' : fields.many2one('stock.prorate','Prorate Reference'),
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:context={}
        cntxt = context.copy()
        new_id = super(stock_move, self).copy(cr, uid, id, default, context=context)
        old_obj = self.browse(cr, uid, id, context)
        new_obj = self.browse(cr, uid,new_id, context)
        if new_obj.prorate_id and old_obj.state not in ['done','cancel'] and not cntxt:
            self.write(cr, uid, id, {'prorate_id':False})
        else:
            self.write(cr, uid, new_id, {'prorate_id':False})
        return new_id
stock_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
