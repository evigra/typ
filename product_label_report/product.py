# -*- encoding: utf-8 -*-
from openerp.osv import fields, osv

class product_label_info(osv.osv):
	_name = 'product.product'
	_inherit = 'product.product'
	_columns = {
		'generic_name': fields.char('Nombre Generico', size=50 , help="nombre generico del articulo"),
		'sale_qty_multiple': fields.integer('Cantidad de venta'),#sistema ver lista de unidad de medida campo
		'sale_unit': fields.many2one('product.uom','UM de venta'),
		'product_country': fields.many2one('res.country','Pais origen'),
		'risk_advices': fields.text('Riesgos de manejo', size=200),
		'handle': fields.text('Instrucciones de uso', size=200),
		'electric_info': fields.text('Caracteristicas electricas', size=200),
		'label_size': fields.selection(
            (('Grande','Grande'),('Mediana','Mediana'),('Chica','Chica')),'Tamaño Etiqueta'),
	}
product_label_info()

class country_asignment(osv.osv):
    _name = 'res.country'
    _inherit ='res.country'
    _columns = {
       'country_id': fields.one2many('product.product','product_country','Pais origen'),
        }

class product_uom_asignment(osv.osv):
	_name = 'product.uom'
	_inherit = 'product.uom'
	_columns = {
		'uom_id': fields.one2many('product.product','sale_unit','UM de venta'),
	}		