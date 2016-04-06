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

import logging
from datetime import datetime
import time

from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _

import openerp.addons.decimal_precision as dp



class product_cost_multicompany(osv.osv):
    _name = "product.cost_multicompany"
    _description = "Product Cost Multicompany"
    
    _rec_name = "product_id"
    
    _columns = {
        'product_id'     : fields.many2one('product.product', 'Product', required=True, select=True),        
        'company_id'     : fields.many2one('res.company', 'Company', required=True,  select=True),
        'standard_price' : fields.float('Cost', digits_compute=dp.get_precision('Product Price'), help="Cost price of the product", groups="base.group_user"),
    }
    
    _defaults = {
        'standard_price': 0.0,
    }
    
    _order = "company_id, product_id"
    
    _sql_constraints = [
        ('product_company_uniq', 'unique(company_id, product_id)', 'The product cost must be unique per company!'),
    ]

class product_product(osv.osv):
    _inherit = 'product.product'

    def _get_standard_price(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for p in self.browse(cr, uid, ids, context=context):
            #if p.cost_method == 'standard':
            #    res[p.id] = p.standard_price2
            #else:
            product_price_obj = self.pool.get('product.cost_multicompany')
            price_id = product_price_obj.search(cr, uid, [('product_id','=',p.id), ('company_id','=',self.pool.get('res.users').browse(cr, uid, uid).company_id.id)])            
            res[p.id] = product_price_obj.read(cr, uid, price_id)[0]['standard_price'] if price_id else 0.0
        return res
    
    _columns = {
        'standard_prices'   : fields.one2many('product.cost_multicompany', 'product_id', string="Standard Price"),
        'standard_price'    : fields.function(_get_standard_price, type='float', string='Cost', digits_compute=dp.get_precision('Product Price'), help="Cost price of the product used for standard stock valuation in accounting and used as a base price on purchase orders.", groups="base.group_user"),
                }
    
    def write(self, cr, uid, ids, vals, context=None):
        if 'standard_price' in vals:
            company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
            product_price_obj = self.pool.get('product.cost_multicompany')
            for product in self.browse(cr, uid, ids):
                price_id = product_price_obj.search(cr, uid, [('product_id','=',product.id), ('company_id','=',company_id)])
                if price_id:
                    product_price_obj.write(cr, uid, price_id, {'standard_price': vals['standard_price']})
                else:
                    res = product_price_obj.create(cr, uid, {'company_id' : company_id, 'product_id' : product.id, 'standard_price' : vals['standard_price']})
            vals.pop('standard_price', None)
        return super(product_product, self).write(cr, uid, ids, vals, context=context)

        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
