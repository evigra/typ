# -*- encoding: utf-8 -*-
{
	'name': 'Asociacion de campos en Reclamaciones',
	'version': '1.0',
	'author': 'Omar Mejia Villavicencio',
	'category': 'TyP',
	'description': """
			Este modulo agregara campos adicionales : 
			1. Producto
			2. Cantidad reclamada
			3. No de Serie
			4. Proveedor
			5. Factura
			6. Orden de compra
	 """,
	 'website': 'http://www.typrefrigeracion.com.mx',
	 'license': 'AGPL-3',
	 'depends': ['product','base','account','crm_claim','purchase','campo_importancia'],
	 'update_xml': [
	 		'crm_view.xml',
	 ],
	 'installable': True,
	 'active': False,
}