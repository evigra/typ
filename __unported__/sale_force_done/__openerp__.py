# -*- encoding: utf-8 -*-

{
    'name': 'Forzar Pedido a Realizado',
    'version': '1',
    "author" : "Argil C.",
    "category" : "TyP",
    'description': """

        Agrega un Boton Cerrar Pedido si esta en estado Abierto:
         - Albaran Entregado.
         - Factura Pagada.

    """,
    "website" : "http://www.argil.mx/",
    "license" : "AGPL-3",
    "depends" : ["sale","stock","account"],
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
