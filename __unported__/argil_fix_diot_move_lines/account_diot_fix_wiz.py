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



class account_move_line_diot_fix(osv.osv_memory):

    """ To create a copy of Waybill when cancelled"""

    _name = 'account.move.line.diot_fix'
    _description = 'Try to fix DIOT Report Move Lines'


    def fix_diot_move_lines(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        record_ids =  context.get('active_ids',[])
        if not record_ids:
            return False
        acc_ml_obj = self.pool.get('account.move.line')
        acc_m_obj = self.pool.get('account.move')
        for line in acc_ml_obj.browse(cr, uid, record_ids):
            amount_line = (line.debit or line.credit) /\
                (line.tax_id_secondary.tax_category_id.value_tax or\
                line.tax_id_secondary.amount)
            difference_amount = abs(amount_line) - abs(line.amount_base)
            if abs(difference_amount) > 0.2:                
                move_state = line.move_id.state
                if move_state == 'posted':
                    acc_m_obj.button_cancel(cr, uid, [line.move_id.id]) 
                for xline in line.move_id.line_id:
                    if (xline.debit == line.debit or xline.credit == line.debit):
                        valor = round((line.amount_base * line.tax_id_secondary.amount), 2)
                        acc_ml_obj.write(cr, uid, xline.id, {('debit' if xline.debit else 'credit'):valor})
                if move_state == 'posted':
                    acc_m_obj.button_validate(cr, uid, [line.move_id.id])
        #raise osv.except_osv('Pausa','Pausa')
        return True


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
