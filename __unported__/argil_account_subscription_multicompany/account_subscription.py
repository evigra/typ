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

import time

from openerp.osv import fields, osv


class account_subscription(osv.osv):
    _inherit = 'account.subscription'

    def _company_default_get(self, cr, uid, model, context=None):
        if not context:
            context = {}
        pool_obj = self.pool.get(model)
        pool_ids = pool_obj.search(cr, uid, [('id','=',uid)])
        pool = pool_obj.browse(cr, uid, pool_ids, context=context)[0]
        if pool.company_id.id:
            return pool.company_id.id

    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    _defaults = {
        'company_id': lambda self, cr, uid, ctx: self._company_default_get(cr, uid, 'res.users', context=ctx)
    }
account_subscription()

class account_subscription_line(osv.osv):
    _inherit = 'account.subscription.line'

    _columns = {
        'company_id'    : fields.related('subscription_id','company_id',type='many2one',relation='res.company',string='Company',store=True,readonly=True),
        }
               

class account_subscription_generate(osv.osv_memory):

    _inherit = "account.subscription.generate"

    def action_generate(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        moves_created=[]
        for data in  self.read(cr, uid, ids, context=context):
            cr.execute('select id from account_subscription_line where date<%s and move_id is null and company_id=%s', (data['date'],self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id))
            line_ids = map(lambda x: x[0], cr.fetchall())
            moves = self.pool.get('account.subscription.line').move_create(cr, uid, line_ids, context=context)
            moves_created.extend(moves)
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_move_line_form')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = str([('id','in',moves_created)])
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: