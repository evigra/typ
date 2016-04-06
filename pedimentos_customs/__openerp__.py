# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 german_442
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)
############################################################################
#    Coded by: german_442 email: (cherman.seingalt@gmail.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Pedimentos Aduanales',
    'version': '1',
    "author" : "Argil Consulting",
    "category" : "TyP",
    'description': """

            Este modulo agrega un formulario de Registro de Pedimentos Aduanales en el Apartado de Compras.
            Compras:\n
                --> Se tiene un Apartado Pedimentos en el Cual Encontramos 2 Opciones.\n
                    * Un Apartado para ver la Definicion de los Pedimentos en forma de Lista.\n
                    * Un Apartado de configuracion para Definicion de Secuencias de Pedimentos.\n
            Almacen:\n
                --> Al Darle Entrada a un Producto, podemos Asignarle a la Recepcion un Pedimiento Aduanal, este Pedimento se llevara hasta el momento de darle Salida al Producto. \n
                    El Modulo Asigna los Numeros de Pedimentos de acuerdo a la Fecha en que se crearon las Secuencias, dandole prioridad de salida a las mas "Antiguas". \n
            Facturacion:\n
                --> Al Crear una Factura desde el pedido de Venta y alguno de los productos tiene algun Pedimento, este se Asigna y se lleva la Informacion al XML.\n

            Para el Manejo de Facturas que no vienen de Ningun pedido, se crearon 2 campos Booleanos en la Ficha Otra Informacion de la Factura los cuales son:\n
                --> Asignacion Automatica Series: Esta Opcion Genera el Albaran de Salida de Forma Automatica y Asigna los Pedimentos y No. de Serie para ese Albaran y de Forma Automatica, los Asigna al XML.\n
                --> Ignorar Series: Para el manejo de alguna Excepcion en donde no sea necesario la asignacion de Pedimentos, se activara esta casilla y el flujo seguira normal para la Facturacion.\n
        
            Pedimentos Manuales: \n
                --> Podemos Cargar los Pedimentos Dando Click al Final de la Linea de Factura a un icono gris en forma de engranes, para asignar los Pedimentos, manualmente.
                    Esto Solo Aplicara para las Lineas de Factura que no tengan Producto.
        Notas: 
                - Si se crea una Factura y algun producto necesita Pedimento ó Serie se tiene que utilizar activa una de las opciones anteriores.
                - Tambien tenemos que tomar en cuenta los Pedidos de Venta que se Facturan desde Movimientos de Salida.
    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    #"depends" : ["purchase","account","l10n_mx_facturae","l10n_mx_facturae_pac_sf","l10n_mx_ir_attachment_facturae","argil_purchase_prorate"],
    "depends" : ["purchase","account","l10n_mx_facturae_base","l10n_mx_facturae","l10n_mx_facturae_pac_sf","l10n_mx_facturae_report","argil_purchase_prorate"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'customs_view.xml',
                    # 'purchase_view.xml',
                    'product_view.xml',
                    #'wizard_account_custom_view.xml',
                    'account_view.xml',
                    'stock_prorate_view.xml',
                    'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
