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
from openerp.tools.translate import _


####### CREAMOS POR HERENCIA UN MODELO DE PEDIDOS DE VENTA PARA MOSTRADOR ####
####### HEREDA DEL MODELO BASE account.invoice ########
class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    _columns = {
        }

    _defaults = {  
        }
    def action_cancel(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.move_id:
                rec.move_id.button_cancel()
                cr.execute("update account_invoice set move_id=null where id=%s ;" % rec.id)
                cr.execute("delete from account_move where id=%s ;" % rec.move_id.id)
        result = super(account_invoice, self).action_cancel(cr, uid, ids, context)
        
                
        return result
account_invoice()
