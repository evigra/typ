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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_location_report_filter(osv.osv_memory):
    _name = "stock.location.report_filter"
    _description = "Products by Location Filters"
    _columns = {
        'location_ids'      : fields.many2many('stock.location','location_contentx_rel','location_id','location_content_wizard_id','Ubicaciones'),
        'product_ids'       : fields.many2many('product.product','product_content_rel','product_id','product_content_wizard_id','Productos'),
        'product_categ_ids' : fields.many2many('product.category','category_content_rel','category_id','category_content_wizard_id','Categorías'),
        'product_name'      : fields.char('Producto parecido a', size=64),
        'report_type'       : fields.selection([
                                          ('1','Contenido de Ubicación'), 
                                          ('2','Resumen Inventario Ubicación'), 
                                          ], 'Reporte', required=True,),
        'reporte_bool': fields.boolean('Reporte Refacciones Soporte'),
        }
    
    _defaults = {
        'report_type' : '1',
        'reporte_bool' : False,
        }

    def do_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        dir_report = ""
        wiz_data = self.browse(cr, uid, ids)[0]
        if not wiz_data.location_ids and not (wiz_data.product_ids or wiz_data.product_categ_ids or wiz_data.product_name):
            raise osv.except_osv(_('Advertencia'), _('No se ha definido ningún parámetro a procesar...'))
        prod_obj = self.pool.get('product.product')
        categ_obj = self.pool.get('product.category')
        product_ids = False
        if wiz_data.product_name:
            prod_ids = prod_obj.search(cr, uid, [('name','ilike',wiz_data.product_name)])
            product_ids = prod_ids or False
        elif wiz_data.product_ids:
            product_ids =  wiz_data.product_ids
        elif wiz_data.product_categ_ids:
            categ_ids = [x.id for x in wiz_data.product_categ_ids]
            categ_ids = categ_obj.search(cr, uid, [('id','child_of',categ_ids)])
            prod_ids = prod_obj.search(cr, uid, [('categ_id','in', tuple(categ_ids),)])
            product_ids = prod_ids or False
        
        if product_ids:
            sql = "drop table if exists _erase_me_content_product_ids; create table _erase_me_content_product_ids (id int not null);"
            for product in product_ids:
                sql += "insert into _erase_me_content_product_ids (id) values (%s);" % (product)
            cr.execute(sql)
        if wiz_data.report_type=='1':
            dir_report = 'lot.stock.overview_all'
        if wiz_data.report_type=='2':
            dir_report = 'lot.stock.overview'
        if wiz_data.reporte_bool:
            dir_report = 'lot.stock.refacciones'
        return  {
            'type': 'ir.actions.report.xml',
            'report_name': dir_report,
            'datas': {
                        'model' : 'stock.location',
                        'ids'   : [x.id for x in wiz_data.location_ids],
                        }
                    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
