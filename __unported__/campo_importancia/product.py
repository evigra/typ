# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'

    #Agregamos el campo al formulario producto o a la tabla product_product
    _columns = {
                'importancia': fields.property(type='char', size=5, string="Importancia"),
                'state_property': fields.property(type="many2one", relation="product.state", string="Estado", help="This field tells the product's state per company"),
        }

class product_state(osv.osv):
    _name = 'product.state'
    _columns = {
        'name':fields.char('Nombre', size=20),
    }
