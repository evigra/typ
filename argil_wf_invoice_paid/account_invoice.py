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


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def test_paid(self, cr, uid, ids, *args):
        for invoice in self.browse(cr, uid, ids):
            if not invoice.residual:
                return True
        res = self.move_line_id_payment_get(cr, uid, ids)
        if not res:
            return False
        ok = True
        any_reconcile = False
        cr.execute('select move_id from account_invoice where id in %s', (tuple(ids),))
        move_id = cr.fetchone()[0]
        if move_id:
            for m in self.pool.get('account.move').browse(cr, uid, move_id).line_id:
                if m.reconcile_id or m.reconcile_partial_id:
                    any_reconcile = True
                    break
        for id in res:
            cr.execute('select reconcile_id from account_move_line where id=%s', (id,))
            res1 = bool(cr.fetchone()[0])
            cr.execute('select count(*) from account_invoice where id in %s and residual < 0.01', (tuple(ids),))
            res2 = any_reconcile and bool(cr.fetchone()[0]) 
            ok = ok and  (res1 or res2)
        return ok

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
