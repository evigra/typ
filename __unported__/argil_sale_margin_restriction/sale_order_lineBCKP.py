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

    def _check_minimal_margin(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        cr.execute("""select usr.id, usr.login, grp.id, grp.name
                        from res_users usr
	                        inner join res_groups_users_rel rel on rel.uid=usr.id
	                        inner join res_groups grp on grp.id=rel.gid and grp.name='Puede vender debajo del margen minimo'
                        where usr.id=%s;""" % (uid))
        res = cr.fetchone()
        #print "res: ", res
        if not res:
            val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sale_minimal_margin', context=context)
            xval = float(val) or 0.0
            #print "xval: ", xval
            for line in self.browse(cr, uid, ids, context=context):
                #print "line.purchase_price * (1.0 + xval/100): ", line.purchase_price * (1.0 + xval/100)
                if line.state=='draft' and line.price_unit < (line.purchase_price * (1.0 + xval/100)) and line.name[0] != '>':
                    return False
        return True
    
    _constraints = [
        (_check_minimal_margin, 'No puede vender el producto con menos del margen estipulado por la empresa, por favor verifique su precio de venta', ['price_unit']),
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
