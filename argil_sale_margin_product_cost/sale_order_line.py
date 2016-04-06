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
import openerp.addons.decimal_precision as dp
import openerp


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
        
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if not context.get('argil_flag', False):
            vals.pop('purchase_price', None)
            frm_cur = self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
            for line in self.browse(cr, uid, ids):
                if not line.product_id:
                    continue
                to_cur = line.order_id.pricelist_id.currency_id.id
                purchase_price = line.product_id.standard_price
                price = self.pool.get('res.currency').compute(cr, uid, frm_cur, to_cur, purchase_price, round=False) or 0.0
                if line.state=='draft' or ('state' in vals and vals['state'] in ('sent', 'waiting_date', 'progress', 'confirmed')):
                    context.update({'argil_flag': 1})
                    self.write(cr, uid, [line.id], {'purchase_price': price}, context=context)
                    context.pop('argil_flag', None)
        return super(sale_order_line, self).write(cr, uid, ids, vals, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
