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

from openerp.osv import osv, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from openerp.tools.translate import _

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
        'broker_log_ids': fields.one2many('purchase.order.broker_log','purchase_id','Brokers Log', readonly=False, 
                                          ),
        'country_name': fields.related('partner_id', 'country_id','name', string='Country', type="char",size=64),
    }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id):
        partner = self.pool.get('res.partner')
        
        res = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id)
        if not partner_id:
            return res
        supplier = partner.browse(cr, uid, partner_id)
        res['value'].update({'country_name':supplier.country_id and supplier.country_id.name or ''})
        return res
    
purchase_order()

class purchase_broker_log(osv.osv):
    _name = "purchase.order.broker_log"
    _description = "Manage purchase travel history"
    _rec_name = 'partner_id'
    
    def _get_spend_time(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for log in self.browse(cr, uid, ids, context=context):
            time_spend = 0.0
            if log.date_arrival and log.date_departure:
               duration = datetime.strptime(log.date_departure, DEFAULT_SERVER_DATETIME_FORMAT) - \
                    datetime.strptime(log.date_arrival, DEFAULT_SERVER_DATETIME_FORMAT)
               days, seconds = duration.days, duration.seconds
               time_spend = days *24 + duration.seconds/float(60*60)
            res[log.id] = time_spend
        return res
    
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True,
                                      domain=[('broker','=',True)], 
                                      help='This is the forwarding Agent(Broker)'),
        'date_arrival': fields.datetime('Arrival Date', help="Arrival Date to Customs"),
        'date_departure': fields.datetime('Departure Date', help="Released Date from customs"),
        'time_custom': fields.function(_get_spend_time, string="Time Spent", type="float", 
                                       help="Time Spent in Customs(Hours between Departure "\
                                       "and Arrival Dates)"),
        'customs_port': fields.char("Customs Port", size=128,required=True),
        'notes': fields.text("Notes"),
        'purchase_id': fields.many2one('purchase.order','Purchase Order', help="Related Purchase order")
    }
    
    def change_date(self, cr, uid, ids, arrival, departure, context=None):
        res = {}
        res['value'] = {}
        res['warning'] = {}
        if arrival and departure:
            if (datetime.strptime(departure, DEFAULT_SERVER_DATETIME_FORMAT) - 
                    datetime.strptime(arrival, DEFAULT_SERVER_DATETIME_FORMAT)).seconds < 0.0:
                res['warning'] = {
                    'title': _('Warning!'),
                    'message': _('Please check the arrival and departure date.')
                }
                res['value'] = {'date_departure': False}
        return res
purchase_broker_log()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
