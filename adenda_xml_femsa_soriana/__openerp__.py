# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://www.hesatecnica.com.com/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@hesatecnica.com)
############################################################################
#    Coded by: german_442 email: (german.ponce@hesatecnica.com)
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
    'name': 'Addenda Femsa y Soriana',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "TyP",
    'description': """

        FEMSA:\n
            Este modulo permite que al generar la Validacion de Una Factura, en el proceso de la Generacion del Archivo XML, se agrega una Addenda FEMSA.\n
            1. En la definicion del Cliente FEMSA en la Pestaña Ventas y Compras, se activa Addenda FEMSA.\n
            2. Dentro del Cliente Debemos Indicar el No. de Proveedor que tenemos Asignado.\n
            3. Al Capturar la Factura al Seleccionar el cliente, el sistema Verifica si es de Femsa, debemos agregar los datos:\n
                - No. Sociedad
                - No. Pedido
                - No. Entrada
                - No. Remision
                - No. Socio Opcional <!-- Opcional -->
                - Centro de Costos <!-- Opcional -->
                - Fecha Inicio de Liquidacion <!-- Opcional -->
                - Fecha Fin de Liquidaciones <!-- Opcional -->
                - Retenciones <!-- Opcional -->

            Nota: Solo se generara la Addenda para aquellos Clientes con el CheckBox de Addenda FEMSA Activada y con la Informacion Requerida. \n
    
        SORIANA:\n
            Este modulo permite que al generar la Validacion de Una Factura, en el proceso de la Generacion del Archivo XML, se agrega una Addenda SORIANA  .\n
            1. En la definicion del Cliente SORIANA en la Pestaña Ventas y Compras, se activa Addenda SORIANA.\n
            2. Dentro de la Ficha de Cliente debemos Ingresar Nuestro Numero de Proveedor que nos Asigno Soriana.\n
            3. Para Finalizar Debemos Capturar los datos extra para la Addenda dentro de la Factura:\n
                - Cliente SORIANA
                - No. de Remision
                - Fecha de Remision
                - Tienda Entrega
                - Tipo Bulto
                - Cantidad de Bultos
                - Cantidad de Pedidos
                - Fecha de Entrega
                - No. de Pedido
            Nota: Solo se generara la Addenda para aquellos Clientes con el CheckBox de Addenda SORIANA Activada y con la Informacion Requerida.
    
        ADDENDA MANUAL:\n
            Este modulo soporta Ingresar una Addenda Manualmente para ello:\n
            - Activar Addenda Manual en la Ficha Otra Informacion.
            - Por Ultimo se Necesita Ingresar el XML de la Addenda como el siguiente Ejemplo:
            \n
            <cfdi:Addenda><GPC:HondaPartes asn="00000713" fecha="20141101" folio="F0028" moneda="MXN" tipoComprobante="FACTURA" tipoDocumento="GPC" unidadDeNegocio="HCL" xmlns:GPC="http://www.honda.net.mx/GPC"><GPC:Proveedor categoria="00000" numeroProveedor="51915202" rfc="NCM1111019H6"/><GPC:Conceptos><GPC:Concepto cantidad="480" descripcion="SEAL FR DOOR INNER" importe="2597.71" noIdentificacion="72315-T5RA010-M2" nolinea="1" ordenCompra="00S-055552" unidad="PIEZAS" valorUnitario="5.4119"/><GPC:Concepto cantidad="510" descripcion="SEAL FR DOOR INNER" importe="2760.07" noIdentificacion="72355-T5RA010-M2" nolinea="2" ordenCompra="00S-055552" unidad="PIEZAS" valorUnitario="5.4119"/><GPC:Concepto cantidad="960" descripcion="SEAL FR DOOR INNER" importe="4642.37" noIdentificacion="72815-T5RA010-M2" nolinea="3" ordenCompra="00S-055552" unidad="PIEZAS" valorUnitario="4.8358"/></GPC:Conceptos></GPC:HondaPartes></cfdi:Addenda>
            - Al Validar la Factura Podremos Observar que conlleva esa Addenda Insertada en el XML.


    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","pedimentos_customs","l10n_mx_facturae_base","l10n_mx_facturae_pac_sf","l10n_mx_ir_attachment_facturae"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "security/ir.model.access.csv",
                    "res_partner_view.xml",
                    "addenda_view.xml",
                    # "sale_view.xml",
                    # "picking_view.xml",
                    ],
    "installable" : True,
    "active" : False,
}
