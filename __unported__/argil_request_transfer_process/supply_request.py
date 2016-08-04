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
###############a###############################################################

from openerp.osv import osv, fields

class stock_supply_request(osv.osv):
    _inherit = "stock.supply_request"
    _columns = {
        'transfer_id': fields.integer('Transfer ID'),
        'transfer_line_id': fields.integer('Transfer Line ID',),
        'state': fields.selection([('draft', 'Draft'), ('confirm','Confirmed'), 
                                   ('wait','Waiting for Transfer'),('ready','Ready to Receive'),
                                   ('done', 'Done'), ('cancel','Cancel')], 'State'),
        'back_supply_req_id': fields.many2one('stock.supply_request','Backorder'),
    }
    _defaults = {
        'transfer_id':0,
        'transfer_line_id':0
    }
        
stock_supply_request()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
