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
    'name': 'Fletes x Sucursal - Reclasificación automática',
    'version': '1',
    "author" : "Argil Consulting - German Ponce Dominguez",
    "category" : "TyP",
    'description': """

Contexto:
======================= 
        * En TyP tienen 10 sucursales.
        * Tienen muchos envíos del CEDis a las sucursales. El gasto de cada sucursal debe quedar registrado en la sucursal y "cargado" (Gasto) en la Sucursal.
        * Sin embargo el Transportista hace una sola Factura por TODOS los envíos del CEDis hacia las sucursales. Lo que genera que el Gasto quede registrado actualmente en el CEDis y no en las sucursales.
        * En TyP, para los Pedidos de Compra de Fletes usan el método de Facturación "Basado en Líneas de Pedidos de Compra", por lo que para generar la factura usan la opción Compras => Control de Facturas => En las líneas del Pedido de Compra
        Desde allí seleccionan TODOS los pedidos de compra y generan la factura en el CEDis.\n
        Esto acarrea el siguiente problema, cada línea seleccionada de "x" sucursal trae los impuestos de la sucursal, por consiguiente, cada línea de la sucursal "x" se tiene que editar para cambiar los impuestos por los que corresponden en el CEDis.

Configuracion:
======================= 
        * Productos, pestaña Contabilidad, campo Cuenta de Reclasificacion de Gasto, aqui debemos agregar una Cuenta para Cada Compañia (Sucursal) con la cual podremos Crear los Asientos Contables de Reclasificacion.
        * Categoria de Productos, Tenemos el campo Cuenta de Reclasificacion de Gasto, es el mismo campo Anterior debemos Crear una cuenta para cada Compañia (Sucursal), en caso de que el Producto no tenga la cuenta se tomara esta en su lugar.
        * Contabilidad --> Proveedores --> Reclasificacion de Fletes. Aqui tenemos que definir las Cuentas que se tomaran para la Reclasificacion.
            - Primero debemos Crear un registro poniendo la Compañia principal (Cedis).
            - Debemos crear cuentas en esa Compañia, para cada Tienda que vamos a reclasificar.
            - Estas Cuentas Pertenecen a la Compañia principal de la Configuracion, solo hacemos referencia a que compañia pertenecera.

:La Configuracion de Reclasificacion debe quedar como la siguiente Imagen: \n

.. image:: /reclassification_automatic_fleet/static/src/img/rec_config.png

:Nota:
:Las cuentas que se muestran en la Imagen Pertenecen a la Compañia Padre definida en el Registro de Configuracion.

    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","purchase","stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    # "stock_view.xml",
                    "account_view.xml",
                    "reclasification_config_view.xml",
                    ],
    "installable" : True,
    "active" : False,
}
