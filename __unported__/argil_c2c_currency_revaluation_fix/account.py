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


class account_account(osv.osv):
    _inherit = 'account.account'

    def _revaluation_query(self, cr, uid, ids,
                           revaluation_date,
                           context=None):

        context_argil = context.copy()
        context_argil.update({'argil_revaluation' : 1})

        lines_where_clause = self.pool.get('account.move.line').\
            _query_get(cr, uid, context=context_argil)

        query = ("SELECT l.account_id as id, l.partner_id, l.currency_id, " +
                 ', '.join(self._sql_mapping.values()) +
                 " FROM account_move_line l "
                 " WHERE l.account_id IN %(account_ids)s AND "
                 " l.date <= %(revaluation_date)s AND "
                 " l.currency_id IS NOT NULL AND "
                 " l.reconcile_id IS NULL AND "
                 + lines_where_clause + " and l.company_id = " + str(self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id) +
                 " GROUP BY l.account_id, l.currency_id, l.partner_id")
        params = {'revaluation_date': revaluation_date,
                  'account_ids': tuple(ids)}
        return query, params


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
