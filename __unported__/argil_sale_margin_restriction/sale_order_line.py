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


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _check_minimal_margin(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, [uid])[0]
        cr.execute("""select usr.id, usr.login, grp.id, grp.name
                        from res_users usr
                            inner join res_groups_users_rel rel on rel.uid=usr.id
                            inner join res_groups grp on grp.id=rel.gid and grp.name='Puede vender debajo del margen minimo'
                        where usr.id=%s;""" % (uid))
        res = cr.fetchone()
        #print "res: ", res
        self_br = self.browse(cr, uid, ids, context=None)[0]
        if not res:
            if self_br.order_id.state != 'draft':
                return True
            val = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sale_minimal_margin', context=context)
            xval = float(val) or 0.0
            #print "xval: ", xval
            #for line in self.browse(cr, uid, ids, context=context):
                #print "line.purchase_price * (1.0 + xval/100): ", line.purchase_price * (1.0 + xval/100)
                # if line.state=='draft' and line.price_unit < (line.purchase_price * (1.0 + xval/100)) and line.name[0] != '>':
            pricelist_obj = self.pool.get('product.pricelist')
            if not self_br.order_id.pricelist_id or not self_br.product_id:
                return True
            pricelist_id = self_br.order_id.pricelist_id.id
            product_id = self_br.product_id.id
            price_unit = self_br.price_unit
            product_uom_qty = self_br.product_uom_qty
            pricelist_br = self_br.order_id.pricelist_id
            user_obj = self.pool.get('res.users')
            user_br = user_obj.browse(cr, uid, uid,
                context=context)

            prod_obj = self.pool.get('product.product')
            prod_br = self_br.product_id
            parameter = self.pool.get('ir.config_parameter')
            parameter_id = parameter.search(cr, uid, [('key','=',
                                                    'sale_minimal_margin')])
            if parameter_id:
                parameter_br = parameter.browse(cr, uid, parameter_id,
                                                    context=context)[0]
                if prod_br.standard_price:
                    subtotal_sale = self_br.price_subtotal
                    if prod_br.standard_price <= 0.0:
                        return True
                    if prod_br.standard_price == 0.0 and subtotal_sale == 0.0:
                        return True
                    if prod_br.standard_price > 0.0 and subtotal_sale < 0.0:
                        return False
                    if user_br.company_id.currency_id.id == pricelist_br.currency_id.id:
                        purchase_sale = prod_br.standard_price * product_uom_qty
                    else:
                        cr.execute("""select rate from res_currency_rate
                            where currency_id=%s order by name desc""", 
                        (pricelist_br.currency_id.id, ))
                        tipo_cambio = cr.fetchall()[0][0]
                        # tc_int = 1/tipo_cambio
                        # print "############ TC >>>>>> ", tc_int
                        purchase_sale = prod_br.standard_price * product_uom_qty
                        # purchase_sale = purchase_sale / tc_int
                        purchase_sale = purchase_sale * tipo_cambio

                    if purchase_sale == 0.0:
                        return True
                    margin_amount = subtotal_sale - purchase_sale
                    if margin_amount == 0.0:
                        return False
                    # print "#### >>>>>>>>>  MARGEN MONTO >>>> ", margin_amount
                    margin = float(parameter_br.value)
                    try:
                        margin_sale = (margin_amount/subtotal_sale)*100
                    except:
                        return True

                    if margin_sale >= margin:
                        # print "# EL MARGEN ES SUPERIOR O IGUAL AL DEL PARAMETRO >"
                        return True
                    elif margin_sale < 0.0:
                        return False
                    else:
                        return False
                elif prod_br.pack_line_ids:
                    purchase_sale = 0.0
                    #### Validar que todos los componentes del Pack tengan existencia
                    #### Calculando el precio de Coste en base a Componentes del Pack
                    for prod in prod_br.pack_line_ids:
                        purchase_sale+= (prod.product_id.standard_price * prod.quantity)*product_uom_qty
                    if user_br.company_id.currency_id.id == pricelist_br.currency_id.id:
                        purchase_sale = purchase_sale
                    else:
                        cr.execute("""select rate from res_currency_rate
                            where currency_id=%s order by name desc""", 
                        (pricelist_br.currency_id.id, ))
                        tipo_cambio = cr.fetchall()[0][0]
                        purchase_sale = purchase_sale * tipo_cambio

                    subtotal_sale = self_br.price_subtotal
                    margin_amount = subtotal_sale - purchase_sale

                    if margin_amount > 0.0:
                        return True

                    if purchase_sale == 0.0:
                        return True
                    if purchase_sale == 0.0 and subtotal_sale == 0.0:
                        return True
                    if purchase_sale > 0.0 and subtotal_sale < 0.0:
                        return False

                    margin = float(parameter_br.value)
                    try:
                        margin_sale = (margin_amount/subtotal_sale)*100
                    except:
                        return True

                    if margin_sale < margin:

                        return False
        return True
    
    _constraints = [
        (_check_minimal_margin, 'No puede vender el producto con menos del margen estipulado por la empresa, por favor verifique su precio de venta', ['price_unit']),
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
