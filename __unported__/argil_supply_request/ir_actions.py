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

from openerp.osv import fields, osv
from openerp import tools
from openerp import SUPERUSER_ID

class ir_action_window(osv.osv):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        warehouse_pool = self.pool.get('stock.warehouse')
        select = ids
        if isinstance(ids, (int, long)):
            select = [ids]
        res = super(ir_action_window, self).read(cr, uid, select, fields=fields, context=context, load=load)
        for r in res:
            mystring = "'get_supply_warehouse()'"
            if mystring in (r.get('domain', '[]') or ''):
                search_domain = []
                if uid != SUPERUSER_ID:
                    company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
                    search_domain = [('company_id','=',company_id)]
                r['domain'] = r['domain'].replace(mystring, str(warehouse_pool.search(cr, uid,search_domain,context=context)))
        if isinstance(ids, (int, long)):
            if res:
                return res[0]
            else:
                return False
        return res

ir_action_window()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
