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

import time
import datetime
from dateutil.relativedelta import relativedelta

import openerp
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv

class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'
    _columns = {
        'valuation_account_id': fields.many2one('account.account',"Stock Valuation Account",
            help="When real-time inventory valuation is enabled on a product, "\
            "this account will hold the current value of the products."),
        
    }
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        ir_values = self.pool.get('ir.values')
        res = super(account_config_settings, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if 'value' in res:
            valuation_account_id = ir_values.get_default(cr, uid, 'stock.prorate', 'valuation_account_id', company_id=company_id)
            res['value'].update({
                'valuation_account_id': isinstance(valuation_account_id, list) and valuation_account_id[0] or valuation_account_id,
            })
        return res
    
    def set_default_valuation_acc(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)
        ir_values.set_default(cr, SUPERUSER_ID, 'stock.prorate', 'valuation_account_id',
            config.valuation_account_id and config.valuation_account_id.id or False, company_id=config.company_id.id)
account_config_settings()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
