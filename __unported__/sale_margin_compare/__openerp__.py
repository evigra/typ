# -*- encoding: utf-8 -*-

{
    'name': 'Comparacion de Ventas vs Margen',
    'version': '1',
    "author" : "Argil C.",
    "category" : "TyP",
    'description': """

        Al agregar un producto, en Ventas, comparamos contra el 
        parametro del Sistema:

        - sale_minimal_margin

        En donde el Margen por la Venta debe ser igual o mayor al
        Valor definido del Parametro, ejemplo ventas con un Margen
        superior al 15 %.

    """,
    "website" : "http://www.argil.mx/",
    "license" : "AGPL-3",
    "depends" : ["sale",],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                "sale_view.xml",
                    ],
    "installable" : True, # Permite al usuario instalar el Modulo.
    "active" : False,
    # "autoinstall": True, Instalado automaticamente
    #                       cuando se crea una BD
}
