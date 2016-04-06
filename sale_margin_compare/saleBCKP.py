# -*- encoding: utf-8 -*-

#### 
from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID

#### HERENCIA DE PEDIDOS DE VENTA
class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit ='sale.order'
    _columns = {
        }

    _defaults = {
        }

##### HERENCIA DE LINEAS DE VENTA
class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit ='sale.order.line'
    _columns = {
        }

    _defaults = {
        }

    def on_change_margin(self, cr, uid, ids, product_id,
                 product_uom_qty, price_unit, type,
                 pricelist_id, context=None):

        if not product_id:
            return {}
        if type == 'make_to_stock':
            
            group_obj = self.pool.get('res.groups')
            group_id = group_obj.search(cr, uid, [('name','=',
                'Puede vender debajo del margen minimo')])
            if group_id:
                ##### MANERA CONVENCIONAL RECORRIENDO LOS MODELOS
                user_list = []
                for group in group_obj.browse(cr, uid, group_id, context=None):
                    for user in group.users:
                        user_list.append(user.id)
                        if user.id == uid:
                            return {}

                ### MANERA VELOZ POR QUERY SQL
                # cr.execute("""select uid from res_groups_users_rel 
                #         where gid in %s
                #     """, (tuple(group_id),))
                # cr_res = cr.fetchall()
                # user_ids = [x[0] for x in cr_res]
                # print "############ GRUPOS QUERY SQL >>>>>>>>>> ", user_ids
                # if uid in user_ids:
                #     return {}

            pricelist_obj = self.pool.get('product.pricelist')
            pricelist_br = pricelist_obj.browse(cr, uid, pricelist_id,
                context=context)
            user_obj = self.pool.get('res.users')
            user_br = user_obj.browse(cr, uid, uid,
                context=context)

            prod_obj = self.pool.get('product.product')
            prod_br = prod_obj.browse(cr, uid, product_id, context=context)
            parameter = self.pool.get('ir.config_parameter')
            parameter_id = parameter.search(cr, uid, [('key','=',
                                                    'sale_minimal_margin')])
            if parameter_id:
                parameter_br = parameter.browse(cr, uid, parameter_id,
                                                    context=context)[0]
                warning = {
                    'title': 'El Producto %s ' % (prod_br.name,),
                    'message':'No puede Venderse por debajo del\
                     Margen Permitido \nContacta al Administrador'}
                res = {}

                if prod_br.standard_price:
                    subtotal_sale = product_uom_qty * price_unit
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

                    margin_amount = subtotal_sale - purchase_sale
                    # print "#### >>>>>>>>>  MARGEN MONTO >>>> ", margin_amount
                    margin = float(parameter_br.value)
                    margin_sale = (margin_amount/purchase_sale)*100
                    if margin_sale >= margin:
                        # print "# EL MARGEN ES SUPERIOR O IGUAL AL DEL PARAMETRO >"
                        return {}
                    elif margin_sale < 0.0:
                        return {'value': res, 'warning':warning }
                    else:
                        return {'value': res, 'warning':warning }
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

                    subtotal_sale = product_uom_qty * price_unit
                    margin_amount = subtotal_sale - purchase_sale
                    if purchase_sale == 0.0:
                        return {}
                    # print "#### >>>>>>>>>  MARGEN MONTO >>>> ", margin_amount
                    margin = float(parameter_br.value)
                    margin_sale = (margin_amount/purchase_sale)*100
                    # print "############# MARGIN SALE >>>>> ", margin_sale
                    if margin_sale >= margin:
                        # print "# EL MARGEN ES SUPERIOR O IGUAL AL DEL PARAMETRO >"
                        return {}
                    elif margin_sale < 0.0:
                        # print "##### ENTRO ACA >>>>"
                        return {'value': res, 'warning':warning }
                    else:
                        return {'value': res, 'warning':warning }
                else:
                    return {}


        return {}
