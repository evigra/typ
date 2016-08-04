# -*- encoding: utf-8 -*-
{
	'name': 'TyP Warehouse fixes',
	'version': '0.1',
	'author': 'Omar Mejia',
	'category': 'TyP',
	'description': """
		Este modulo, hace cambios en stock
		- Agrega filtro y campo calculado de Ubicaciones
	""",
	'website': 'www.typrefrigeracion.com.mx',
	'depends': [
		'stock',
	],
	'data': [
		'stock_move.xml',
	],
	'installable': True
}