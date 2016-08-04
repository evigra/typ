# -*- encoding: utf-8 -*-
{
	'name': 'Consulta de stock y generador de datos',
	'version': '1.0',
	'author': 'author',
	'category': 'TyP',
	'description': """ Este modulo agrega un checkbox para consultar la existencia del producto en todos los almacenes:
					Ubiucacion:  Ventas/Cotizaciones - Consultar Existencias
					Generador de codigos para el reporte de soriana:
					Ubicación : Ventas/Pedios de Ventas o Cotizaciones/Otra informacion <-- boton Generar Codigos
					""",
	'website': 'www.typrefrigeracion.com.mx',
	'license': 'AGPL-3',
	'depends': ['purchase','sale'],
	'update_xml': [
					'sale_view.xml',
					],
	'installable': True,
	'active': False,
}