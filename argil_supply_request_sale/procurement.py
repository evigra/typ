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

class procurement_order(osv.osv):
    _inherit = 'procurement.order'

    def get_supply_request_data(self,cr, uid, order_point, qty,type='manual',
                                move_obj=False,procurement=False, context=None):
        res = super(procurement_order, self).get_supply_request_data(cr, uid, order_point, qty,type,
                                move_obj,procurement, context=None)
        
        if move_obj and move_obj.sale_line_id and move_obj.sale_line_id.type == 'make_to_supply_request' \
            and move_obj.sale_line_id.warehouse_subsidiary_id:
            res.update({'to_warehouse_id' : move_obj.sale_line_id.warehouse_subsidiary_id.id})
        return res
    
    def get_supply_request_data_wo_orderpoint(self,cr, uid, qty,type='manual',
                                move_obj=False,procurement=False, context=None):
        
        res = super(procurement_order, self).get_supply_request_data_wo_orderpoint(cr, uid, qty,type,
                                move_obj,procurement, context=None)
        if move_obj and move_obj.sale_line_id and move_obj.sale_line_id.type == 'make_to_supply_request' \
            and move_obj.sale_line_id.warehouse_subsidiary_id:
            res.update({'to_warehouse_id' : move_obj.sale_line_id.warehouse_subsidiary_id.id})
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
