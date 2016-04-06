# -*- encoding: utf-8 -*-

{
    'name': 'Automatizacion de Facturacion Electronica',
    'version': '1',
    "author" : "Argil C.",
    "category" : "TyP",
    'description': """

        Al Validar la Factura en automatico se realizara lo siguiente:
            - Validacion de Factura.
            - Generacion de XML Timbrado.
            - Generacion de Reporte PDF.
            - Envio al Cliente de los Documentos.
    """,
    "website" : "http://www.argil.mx/",
    "license" : "AGPL-3",
    "depends" : ["account",
                "mail",
                "argil_attachment_cfdi",
                "l10n_mx_facturae",
                "l10n_mx_facturae_base",
                "l10n_mx_ir_attachment_facturae"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [

                    ],
    "installable" : True, # Permite al usuario instalar el Modulo.
    "active" : False,
    # "autoinstall": True, Instalado automaticamente
    #                       cuando se crea una BD
}
