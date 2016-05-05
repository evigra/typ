# -*- encoding: utf-8 -*-
{
	'name': 'TyP Account Invoice Fixes',
	'version': '1',
	'author': 'omejia',
	'category': 'TyP',
	'description': """
		Este modulo esta encargado de solucionar y hacer pequeños cambios en el sistema, que no requiera
		de una intervencion de un proyecto de desarrollo.

		* Activa por defecto la casilla relacionar con factura y lo deja como solo lectura \n
	""",
	'website':'http://www.typrefrigeracion.com.mx',
	'license': 'AGPL-3',
	'depends': [
		'account',
        'argil_typ_comissions'
	],
	'data' : [
		'account_invoice_view.xml',
	],
	'installable': True,
}
