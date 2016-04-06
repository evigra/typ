# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp import release

import time
import os
import base64
# import libxml2
# import libxslt
# import zipfile
# import StringIO
# import OpenSSL
import hashlib
import tempfile
import os
import codecs
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import string
import logging
_logger = logging.getLogger(__name__)
from xml.dom import minidom
from xml.dom.minidom import Document , parse , parseString
# Cambiar el error
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
msg2 = "Contact you administrator &/or to info@vauxoo.com"

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {        
    'orden_compra': fields.char('Orden de Compra', size=128, help='Honda le Indicara que Numero de Orden de Compra tienen que Capturar'),
    'order_id': fields.many2one('sale.order','Pedido de Venta'),
    'asign_automatic_lot_ped': fields.boolean('Asignacion Automatica Series', help='Si se Activa se generara de Forma Automatica el Alabaran de Salida y se Asignaran los Pedimentos y lotes Necesarios, esto tambien ayuda para Incluirlos en el XML.'),
    'ignored_lot_ped': fields.boolean('Ignorar Series', help='Si se Activa no se generara de Forma Automatica el Alabaran de Salida ni se Asignaran los Pedimentos y lotes Necesarios, se ignoraran para poder Validar la Factura y no seran incluidos en el XML'),
    'stock_picking_out': fields.many2one('stock.picking.out','Alabaran Relacionado'),
    }


    def _get_facturae_invoice_dict_data(self, cr, uid, ids, context=None):
    
        if context is None:
            context = {}
        self.insert_pedimento(cr, uid, ids, context=None)
        invoices = self.browse(cr, uid, ids, context=context)
        invoice_tax_obj = self.pool.get("account.invoice.tax")
        invoice_datas = []
        invoice_data_parents = []
        for invoice in invoices:
            invoice_data_parent = {}
            if invoice.type == 'out_invoice':
                tipoComprobante = 'ingreso'
            elif invoice.type == 'out_refund':
                tipoComprobante = 'egreso'
            else:
                raise osv.except_osv(_('Warning !'), _(
                    'Only can issue electronic invoice to customers.!'))
            # Inicia seccion: Comprobante
            invoice_data_parent['cfdi:Comprobante'] = {}
            # default data
            invoice_data_parent['cfdi:Comprobante'].update({
                'xmlns:cfdi': "http://www.sat.gob.mx/cfd/3",
                'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                'xsi:schemaLocation': "http://www.sat.gob.mx/cfd/3 http://www.sat.gob.mx/sitio_internet/cfd/3/cfdv32.xsd",
                'version': "3.2",
            })
            number_work = invoice.number or invoice.internal_number
            invoice_data_parent['cfdi:Comprobante'].update({
                'folio': number_work,
                'fecha': invoice.date_invoice_tz and
                # time.strftime('%d/%m/%y',
                # time.strptime(invoice.date_invoice, '%Y-%m-%d'))
                time.strftime('%Y-%m-%dT%H:%M:%S', time.strptime(
                invoice.date_invoice_tz, '%Y-%m-%d %H:%M:%S'))
                or '',
                'tipoDeComprobante': tipoComprobante,
                'formaDePago': u'Pago en una sola exhibición',
                'noCertificado': '@',
                'sello': '@',
                'certificado': '@',
                'subTotal': "%.2f" % (invoice.amount_untaxed or 0.0),
                'descuento': "0",  # Add field general
                'total': "%.2f" % (invoice.amount_total or 0.0),
            })
            folio_data = self._get_folio(
                cr, uid, [invoice.id], context=context)
            serie = folio_data.get('serie', False)
            if serie:
                invoice_data_parent['cfdi:Comprobante'].update({
                    'serie': serie,
                })
            # Termina seccion: Comprobante
            # Inicia seccion: Emisor
            partner_obj = self.pool.get('res.partner')
            address_invoice = invoice.address_issued_id or False
            address_invoice_parent = invoice.company_emitter_id and \
            invoice.company_emitter_id.address_invoice_parent_company_id or False

            if not address_invoice:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined the address issuing!"))

            if not address_invoice_parent:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined an address of invoicing from the company!"))

            if not address_invoice_parent.vat:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined RFC for the address of invoice to the company!"))

            invoice_data = invoice_data_parent['cfdi:Comprobante']
            invoice_data['cfdi:Emisor'] = {}
            invoice_data['cfdi:Emisor'].update({

                'rfc': (('vat_split' in address_invoice_parent._columns and \
                address_invoice_parent.vat_split or address_invoice_parent.vat) \
                or '').replace('-', ' ').replace(' ', ''),
                'nombre': address_invoice_parent.name or '',
                # Obtener domicilio dinamicamente
                # virtual_invoice.append( (invoice.company_id and
                # invoice.company_id.partner_id and
                # invoice.company_id.partner_id.vat or '').replac

                'cfdi:DomicilioFiscal': {
                    'calle': address_invoice_parent.street and \
                        address_invoice_parent.street.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or '',
                    'noExterior': address_invoice_parent.l10n_mx_street3 and \
                        address_invoice_parent.l10n_mx_street3.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or 'N/A',  # "Numero Exterior"
                    'noInterior': address_invoice_parent.l10n_mx_street4 and \
                        address_invoice_parent.l10n_mx_street4.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or 'N/A',  # "Numero Interior"
                    'colonia':  address_invoice_parent.street2 and \
                        address_invoice_parent.street2.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or False,
                    'localidad': address_invoice_parent.l10n_mx_city2 and \
                        address_invoice_parent.l10n_mx_city2.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or False,
                    'municipio': address_invoice_parent.city and \
                        address_invoice_parent.city.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or '',
                    'estado': address_invoice_parent.state_id and \
                        address_invoice_parent.state_id.name and \
                        address_invoice_parent.state_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'pais': address_invoice_parent.country_id and \
                        address_invoice_parent.country_id.name and \
                        address_invoice_parent.country_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice_parent.zip and \
                        address_invoice_parent.zip.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ').replace(' ', '') or '',
                },
                'cfdi:ExpedidoEn': {
                    'calle': address_invoice.street and address_invoice.\
                        street.replace('\n\r', ' ').replace('\r\n', ' ').\
                        replace('\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice.l10n_mx_street3 and \
                        address_invoice.l10n_mx_street3.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or 'N/A',  # "Numero Exterior"
                    'noInterior': address_invoice.l10n_mx_street4 and \
                        address_invoice.l10n_mx_street4.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or 'N/A',  # "Numero Interior"
                    'colonia':  address_invoice.street2 and address_invoice.\
                        street2.replace('\n\r', ' ').replace('\r\n', ' ').\
                        replace('\n', ' ').replace('\r', ' ') or False,
                    'localidad': address_invoice.l10n_mx_city2 and \
                        address_invoice.l10n_mx_city2.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or False,
                    'municipio': address_invoice.city and address_invoice.\
                        city.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice.state_id and address_invoice.\
                        state_id.name and address_invoice.state_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or '',
                    'pais': address_invoice.country_id and address_invoice.\
                        country_id.name and address_invoice.country_id.name.\
                        replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice.zip and address_invoice.\
                        zip.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ').replace(' ', '') or '',
                },
            })
            if invoice_data['cfdi:Emisor']['cfdi:DomicilioFiscal'].get('colonia') == False:
                invoice_data['cfdi:Emisor']['cfdi:DomicilioFiscal'].pop('colonia')
            if invoice_data['cfdi:Emisor']['cfdi:ExpedidoEn'].get('colonia') == False:
                invoice_data['cfdi:Emisor']['cfdi:ExpedidoEn'].pop('colonia')
            if invoice_data['cfdi:Emisor']['cfdi:DomicilioFiscal'].get('localidad') == False:
                invoice_data['cfdi:Emisor']['cfdi:DomicilioFiscal'].pop('localidad')
            if invoice_data['cfdi:Emisor']['cfdi:ExpedidoEn'].get('localidad') == False:
                invoice_data['cfdi:Emisor']['cfdi:ExpedidoEn'].pop('localidad')
            # Termina seccion: Emisor
            # Inicia seccion: Receptor
            parent_id = invoice.partner_id.commercial_partner_id.id
            parent_obj = partner_obj.browse(cr, uid, parent_id, context=context)
            if not parent_obj.vat:
                raise osv.except_osv(_('Warning !'), _(
                    "Don't have defined RFC of the partner[%s].\n%s !") % (
                    parent_obj.name, msg2))
            if parent_obj._columns.has_key('vat_split') and\
                parent_obj.vat[0:2] <> 'MX':
                rfc = 'XAXX010101000'
            else:
                rfc = ((parent_obj._columns.has_key('vat_split')\
                    and parent_obj.vat_split or parent_obj.vat)\
                    or '').replace('-', ' ').replace(' ','')
            address_invoice = partner_obj.browse(cr, uid, \
                invoice.partner_id.id, context=context)
            invoice_data['cfdi:Receptor'] = {}
            invoice_data['cfdi:Receptor'].update({
                'rfc': rfc,
                'nombre': (parent_obj.name or ''),
                'cfdi:Domicilio': {
                    'calle': address_invoice.street and address_invoice.\
                        street.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'noExterior': address_invoice.l10n_mx_street3 and \
                        address_invoice.l10n_mx_street3.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or 'N/A',  # "Numero Exterior"
                    'noInterior': address_invoice.l10n_mx_street4 and \
                        address_invoice.l10n_mx_street4.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or 'N/A',  # "Numero Interior"
                    'colonia':  address_invoice.street2 and address_invoice.\
                        street2.replace('\n\r', ' ').replace('\r\n', ' ').\
                        replace('\n', ' ').replace('\r', ' ') or False,
                    'localidad': address_invoice.l10n_mx_city2 and \
                        address_invoice.l10n_mx_city2.replace('\n\r', ' ').\
                        replace('\r\n', ' ').replace('\n', ' ').replace(
                        '\r', ' ') or False,
                    'municipio': address_invoice.city and address_invoice.\
                        city.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                    'estado': address_invoice.state_id and address_invoice.\
                        state_id.name and address_invoice.state_id.name.replace(
                        '\n\r', ' ').replace('\r\n', ' ').replace('\n', ' ').\
                        replace('\r', ' ') or '',
                    'pais': address_invoice.country_id and address_invoice.\
                        country_id.name and address_invoice.country_id.name.\
                        replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ')or '',
                    'codigoPostal': address_invoice.zip and address_invoice.\
                        zip.replace('\n\r', ' ').replace('\r\n', ' ').replace(
                        '\n', ' ').replace('\r', ' ') or '',
                },
            })
            if invoice_data['cfdi:Receptor']['cfdi:Domicilio'].get('colonia') == False:
                invoice_data['cfdi:Receptor']['cfdi:Domicilio'].pop('colonia')
            if invoice_data['cfdi:Receptor']['cfdi:Domicilio'].get('localidad') == False:
                invoice_data['cfdi:Receptor']['cfdi:Domicilio'].pop('localidad')
            # Termina seccion: Receptor
            # Inicia seccion: Conceptos
            invoice_data['cfdi:Conceptos'] = []
            for line in invoice.invoice_line:
                # price_type = invoice._columns.has_key('price_type') and invoice.price_type or 'tax_excluded'
                # if price_type == 'tax_included':
# price_unit = line.price_subtotal/line.quantity#Agrega compatibilidad con
# modulo TaxIncluded
                price_unit = line.quantity != 0 and line.price_subtotal / \
                    line.quantity or 0.0
                concepto = {
                    'cantidad': "%.2f" % (line.quantity or 0.0),
                    'descripcion': line.name or '',
                    'valorUnitario': "%.2f" % (price_unit or 0.0),
                    'importe': "%.4f" % (line.price_subtotal or 0.0),  # round(line.price_unit *(1-(line.discount/100)),2) or 0.00),#Calc: iva, disc, qty
                    # Falta agregar discount
                }
                unidad = line.uos_id and line.uos_id.name or ''
                if unidad:
                    concepto.update({'unidad': unidad})
                product_code = line.product_id and line.product_id.default_code or ''
                if product_code:
                    concepto.update({'noIdentificacion': product_code})
                invoice_data['cfdi:Conceptos'].append({'cfdi:Concepto': concepto})

                pedimento = None
                if line.pedimentos_manuales_ids:
                    for pedbr in line.pedimentos_manuales_ids:
                        informacion_aduanera = {
                            'aduana': pedbr.aduana,
                            'fecha': pedbr.fecha,
                            'numero': pedbr.numero,
                        }
                        concepto.update({
                                        'cfdi:InformacionAduanera': informacion_aduanera})
                # Termina seccion: Conceptos
            # Inicia seccion: impuestos
            invoice_data['cfdi:Impuestos'] = {}
            invoice_data['cfdi:Impuestos'].update({
                #'totalImpuestosTrasladados': "%.2f"%( invoice.amount_tax or 0.0),
            })
            invoice_data['cfdi:Impuestos'].update({
                #'totalImpuestosRetenidos': "%.2f"%( invoice.amount_tax or 0.0 )
            })

            invoice_data_impuestos = invoice_data['cfdi:Impuestos']
            invoice_data_impuestos['cfdi:Traslados'] = []
            # invoice_data_impuestos['Retenciones'] = []

            tax_names = []
            totalImpuestosTrasladados = 0
            totalImpuestosRetenidos = 0
            for line_tax_id in invoice.tax_line:
                tax_name = line_tax_id.name2
                tax_names.append(tax_name)
                line_tax_id_amount = abs(line_tax_id.amount or 0.0)
                if line_tax_id.amount >= 0:
                    impuesto_list = invoice_data_impuestos['cfdi:Traslados']
                    impuesto_str = 'cfdi:Traslado'
                    totalImpuestosTrasladados += line_tax_id_amount
                else:
                    # impuesto_list = invoice_data_impuestos['Retenciones']
                    impuesto_list = invoice_data_impuestos.setdefault(
                        'cfdi:Retenciones', [])
                    impuesto_str = 'cfdi:Retencion'
                    totalImpuestosRetenidos += line_tax_id_amount
                impuesto_dict = {impuesto_str:
                                {
                                 'impuesto': tax_name,
                                 'importe': "%.2f" % (line_tax_id_amount),
                                 }
                                 }
                if line_tax_id.amount >= 0:
                    impuesto_dict[impuesto_str].update({
                            'tasa': "%.2f" % (abs(line_tax_id.tax_percent))})
                impuesto_list.append(impuesto_dict)

            invoice_data['cfdi:Impuestos'].update({
                'totalImpuestosTrasladados': "%.2f" % (totalImpuestosTrasladados),
            })
            if totalImpuestosRetenidos:
                invoice_data['cfdi:Impuestos'].update({
                    'totalImpuestosRetenidos': "%.2f" % (totalImpuestosRetenidos)
                })

            tax_requireds = ['IVA', 'IEPS']
            for tax_required in tax_requireds:
                if tax_required in tax_names:
                    continue
                invoice_data_impuestos['cfdi:Traslados'].append({'cfdi:Traslado': {
                    'impuesto': tax_required,
                    'tasa': "%.2f" % (0.0),
                    'importe': "%.2f" % (0.0),
                }})
            # Termina seccion: impuestos
            invoice_data_parents.append(invoice_data_parent)
            invoice_data_parent['state'] = invoice.state
            invoice_data_parent['invoice_id'] = invoice.id
            invoice_data_parent['type'] = invoice.type
            invoice_data_parent['invoice_datetime'] = invoice.invoice_datetime
            invoice_data_parent['date_invoice_tz'] = invoice.date_invoice_tz
            invoice_data_parent['currency_id'] = invoice.currency_id.id

            date_ctx = {'date': invoice.date_invoice_tz and time.strftime(
                '%Y-%m-%d', time.strptime(invoice.date_invoice_tz,
                '%Y-%m-%d %H:%M:%S')) or False}
            currency = self.pool.get('res.currency').browse(
                cr, uid, [invoice.currency_id.id], context=date_ctx)[0]
            rate = currency.rate != 0 and 1.0/currency.rate or 0.0
            invoice_data_parent['rate'] = rate

        invoice_datetime = invoice_data_parents[0].get('invoice_datetime',
            {}) and datetime.strptime(invoice_data_parents[0].get(
            'invoice_datetime', {}), '%Y-%m-%d %H:%M:%S').strftime(
            '%Y-%m-%d') or False
        if not invoice_datetime:
            raise osv.except_osv(_('Date Invoice Empty'), _(
                "Can't generate a invoice without date, make sure that the state of invoice not is draft & the date of invoice not is empty"))
        if invoice_datetime < '2012-07-01':
            return invoice_data_parent
        else:
            invoice = self.browse(cr, uid, ids, context={
                                  'date': invoice_datetime})[0]
            city = invoice_data_parents and invoice_data_parents[0].get(
                'cfdi:Comprobante', {}).get('cfdi:Emisor', {}).get('cfdi:ExpedidoEn', {}).get(
                'municipio', {}) or False
            state = invoice_data_parents and invoice_data_parents[0].get(
                'cfdi:Comprobante', {}).get('cfdi:Emisor', {}).get('cfdi:ExpedidoEn', {}).get(
                'estado', {}) or False
            country = invoice_data_parents and invoice_data_parents[0].get(
                'cfdi:Comprobante', {}).get('cfdi:Emisor', {}).get('cfdi:ExpedidoEn', {}).get(
                'pais', {}) or False
            if city and state and country:
                address = city + ' ' + state + ', ' + country
            else:
                raise osv.except_osv(_('Address Incomplete!'), _(
                    'Ckeck that the address of company issuing of fiscal voucher is complete (City - State - Country)'))

            if not invoice.company_emitter_id.partner_id.regimen_fiscal_id.name:
                raise osv.except_osv(_('Missing Fiscal Regime!'), _(
                    'The Fiscal Regime of the company issuing of fiscal voucher is a data required'))

            invoice_data_parents[0]['cfdi:Comprobante'][
                'TipoCambio'] = invoice.rate or 1
            invoice_data_parents[0]['cfdi:Comprobante'][
                'Moneda'] = invoice.currency_id.name or ''
            invoice_data_parents[0]['cfdi:Comprobante'][
                'NumCtaPago'] = invoice.acc_payment.last_acc_number\
                    or 'No identificado'
            invoice_data_parents[0]['cfdi:Comprobante'][
                'metodoDePago'] = invoice.pay_method_id.name or 'No identificado'
            invoice_data_parents[0]['cfdi:Comprobante']['cfdi:Emisor']['cfdi:RegimenFiscal'] = {
                'Regimen': invoice.company_emitter_id.partner_id.\
                    regimen_fiscal_id.name or ''}
            invoice_data_parents[0]['cfdi:Comprobante']['LugarExpedicion'] = address
        return invoice_data_parents

    ### Asignacion Automatica de Pedimentos
    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=None)
        for order in self.browse(cr, uid, ids, context=context):
            user_br = self.pool.get('res.users').browse(cr, uid, uid, context=None)
            
            if order.type == "out_invoice":
                # origin = order.name
                stock_obj = self.pool.get('stock.picking.out')
                lot_obj = self.pool.get('stock.production.lot.pedimento')
                invoice_products = [x.product_id.id for x in order.invoice_line]
                origin = ""
                if order.origin:
                    if ":" in order.origin:
                        origin=tuple(order.origin.split(":"))
                    else:
                        origin = tuple([str(order.origin)])
                product_pediments = lot_obj.search(cr, uid, [('product_id','in',tuple(invoice_products))])
                list_products = [str(x.product_id.name) for x in lot_obj.browse(cr, uid, product_pediments, context=None)]
                list_products = set(list_products)
                if product_pediments:
                    #picking_out = stock_obj.search(cr, uid, [('name','=',order.origin)])
                    picking_out = []
                    if origin:
                        picking_out = stock_obj.search(cr, uid, [('origin','in',origin),])
                    if not picking_out or not origin:
                        ### Algun Producto Usa pedimentos
                        if order.ignored_lot_ped == False:

                            if order.asign_automatic_lot_ped == False:
                                raise osv.except_osv(_('Error \n Uno de los Productos Utiliza Pedimentos Utiliza una de las Opciones!'), 
                                    _('1. Activa Ignorar Series o \n 2. Asignacion Automatica Series \n En la Pestaña Otra Informacion, \n Productos: %s' %(list(list_products),)))
                        if order.ignored_lot_ped == False and  order.asign_automatic_lot_ped == True:
                            stock_vals = {
                                        'partner_id': order.partner_id.id,
                                        'move_type': 'one',
                                        'company_id': user_br.company_id.id,
                                        'origin': order.number,
                                        }
                            stock_id = stock_obj.create(cr, uid, stock_vals, context=None)
                            for stock in stock_obj.browse(cr, uid, [stock_id], context=None):
                                order.write({'origin': stock.name,'stock_picking_out':stock_id})
                                stock_split_obj = self.pool.get('stock.move.split')
                                for line in order.invoice_line:
                                    ### Ubicacion de Existencias ###
                                    mod_obj = self.pool.get('ir.model.data')
                                    location_xml_id = 'stock_location_stock'
                                    location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                                    ### Ubicacion Clientes ####
                                    location_xml_customer = 'stock_location_customers'
                                    location_customer_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_customer)
                                    qty_lines = line.quantity
                                    lot_disp = lot_obj.search(cr, uid, [('product_id','=',line.product_id.id),('stock_available','>',0.0)])
                                    lot_disp = tuple(lot_disp)
                                    product_id = line.product_id.id
                                    move_lines_lots = []
                                    if lot_disp:
                                        cr.execute("select id from stock_production_lot_pedimento where id in %s order by date", (lot_disp,))
                                        data_ids = [x[0] for x in cr.fetchall()]
                                        cr.execute("select sum(stock_available) from stock_production_lot_pedimento where id in %s", (lot_disp,))
                                        sum_lots_disp = cr.fetchall()[0][0]
                                        while (qty_lines > 0.0):
                                            if sum_lots_disp > 0:
                                                for lote in lot_obj.browse(cr, uid, data_ids, context=None):
                                                    qty_available = lote.stock_available
                                                    qty_asign = 0.0
                                                    if qty_lines > qty_available:
                                                        qty_asign = qty_available
                                                        qty_lines = qty_lines - qty_available
                                                    elif qty_lines <= qty_available:
                                                        qty_asign = qty_lines
                                                        qty_lines = 0.0
                                                    xline = (0,0,{
                                                        'product_id': line.product_id.id,
                                                        'product_uom': line.uos_id.id if line.uos_id else line.product_id.uom_id.id,
                                                        'product_qty': qty_asign,
                                                        'partner_id': order.partner_id.id,
                                                        # 'quantity': qty_asign,
                                                        'pedimento_id': lote.id,
                                                        'name': line.name + " / Pedimento: "+ lote.name,
                                                        'location_id': location_id[1] if location_id else False,
                                                        'location_dest_id': order.partner_id.property_stock_customer.id if order.partner_id.property_stock_customer else location_customer_id[1],
                                                        })
                                                    move_lines_lots.append(xline)
                                                    stock_available_w = lote.stock_available - qty_asign
                                                    lote.write({'stock_available':stock_available_w})
                                                    sum_lots_disp = sum_lots_disp - qty_asign
                                            else:
                                                break
                                ### Escribiendo las Lineas del Albaran ###
                                stock_obj.write(cr, uid, [stock_id], {'move_lines':[x for x in move_lines_lots]})    
        return  res

    def _get_facturae_invoice_xml_data(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_dict = self._get_facturae_invoice_dict_data(
            cr, uid, ids, context=context)[0]
        doc_xml = self.dict2xml({
                                'cfdi:Comprobante': data_dict.get('cfdi:Comprobante')})
        invoice_number = "sn"
        (fileno_xml, fname_xml) = tempfile.mkstemp(
            '.xml', 'openerp_' + (invoice_number or '') + '__facturae__')
        fname_txt = fname_xml + '.txt'
        f = codecs.open(fname_xml,'w','utf-8')
        doc_xml.writexml(
            f, indent='    ', addindent='    ', newl='\r\n', encoding='UTF-8')
        f.close()
        os.close(fileno_xml)

        (fileno_sign, fname_sign) = tempfile.mkstemp('.txt', 'openerp_' + (
            invoice_number or '') + '__facturae_txt_md5__')
        os.close(fileno_sign)

        context.update({
            'fname_xml': fname_xml,
            'fname_txt': fname_txt,
            'fname_sign': fname_sign,
        })
        context.update(self._get_file_globals(cr, uid, ids, context=context))
        fname_txt, txt_str = self._xml2cad_orig(
            cr=False, uid=False, ids=False, context=context)
        data_dict['cadena_original'] = txt_str

        if not txt_str:
            raise osv.except_osv(_('Error en Cadena original!'), _(
                "Can't get the string original of the voucher.\nCkeck your configuration.\n%s" % (msg2)))

        if not data_dict['cfdi:Comprobante'].get('folio', ''):
            raise osv.except_osv(_('Error in Folio!'), _(
                "Can't get the folio of the voucher.\nBefore generating the XML, click on the button, generate invoice.\nCkeck your configuration.\n%s" % (msg2)))

        # time.strftime('%Y-%m-%dT%H:%M:%S',
        # time.strptime(invoice.date_invoice, '%Y-%m-%d %H:%M:%S'))
        context.update({'fecha': data_dict['cfdi:Comprobante']['fecha']})
        sign_str = self._get_sello(
            cr=False, uid=False, ids=False, context=context)
        if not sign_str:
            raise osv.except_osv(_('Error in Stamp !'), _(
                "Can't generate the stamp of the voucher.\nCkeck your configuration.\ns%s") % (msg2))

        nodeComprobante = doc_xml.getElementsByTagName("cfdi:Comprobante")[0]
        nodeComprobante.setAttribute("sello", sign_str)
        data_dict['cfdi:Comprobante']['sello'] = sign_str

        noCertificado = self._get_noCertificado(cr, uid, ids, context['fname_cer'])
        if not noCertificado:
            raise osv.except_osv(_('Error in No. Certificate !'), _(
                "Can't get the Certificate Number of the voucher.\nCkeck your configuration.\n%s") % (msg2))
        nodeComprobante.setAttribute("noCertificado", noCertificado)
        data_dict['cfdi:Comprobante']['noCertificado'] = noCertificado

        cert_str = self._get_certificate_str(context['fname_cer'])
        if not cert_str:
            raise osv.except_osv(_('Error in Certificate!'), _(
                "Can't generate the Certificate of the voucher.\nCkeck your configuration.\n%s") % (msg2))
        cert_str = cert_str.replace(' ', '').replace('\n', '')
        nodeComprobante.setAttribute("certificado", cert_str)
        data_dict['cfdi:Comprobante']['certificado'] = cert_str

        x = doc_xml.documentElement
        nodeReceptor = doc_xml.getElementsByTagName('cfdi:Receptor')[0]
        nodeConcepto = doc_xml.getElementsByTagName('cfdi:Conceptos')[0]
        x.insertBefore(nodeReceptor, nodeConcepto)
        self.write_cfd_data(cr, uid, ids, data_dict, context=context)

        if context.get('type_data') == 'dict':
            return data_dict
        if context.get('type_data') == 'xml_obj':
            return doc_xml
        data_xml = doc_xml.toxml('UTF-8')
        data_xml = codecs.BOM_UTF8 + data_xml
        fname_xml = (data_dict['cfdi:Comprobante']['cfdi:Emisor']['rfc'] or '') + '_' + (
            data_dict['cfdi:Comprobante'].get('serie', '') or '') + '_' + (
            data_dict['cfdi:Comprobante'].get('folio', '') or '') + '.xml'
        data_xml = data_xml.replace('<?xml version="1.0" encoding="UTF-8"?>', '<?xml version="1.0" encoding="UTF-8"?>\n')

        # account_browse = self.browse(cr, uid, ids, context=None)
        # pedimento_xml = self.insert_pedimento(cr, uid, ids, account_browse, data_xml, context=None)

        # print "###################### PEDIMENTO XML", pedimento_xml
        # print "###################### PEDIMENTO XML", pedimento_xml
        # print "###################### PEDIMENTO XML", pedimento_xml
        # if pedimento_xml:
        #     data_xml = pedimento_xml

        date_invoice = data_dict.get('cfdi:Comprobante',{}) and datetime.strptime( data_dict.get('cfdi:Comprobante',{}).get('fecha',{}), '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d') or False
        facturae_version = '3.2'
        try:
            self.validate_scheme_facturae_xml(cr, uid, ids, [data_xml], facturae_version)
        except Exception, e:
            raise orm.except_orm(_('Warning'), _('Parse Error XML: %s.') % (e))
        return fname_xml, data_xml

    def validate_scheme_facturae_xml(self, cr, uid, ids, datas_xmls=[], facturae_version = None, facturae_type="cfdv", scheme_type='xsd'):
    #TODO: bzr add to file fname_schema
        if not datas_xmls:
            datas_xmls = []
        certificate_lib = self.pool.get('facturae.certificate.library')
        for data_xml in datas_xmls:
            (fileno_data_xml, fname_data_xml) = tempfile.mkstemp('.xml', 'openerp_' + (False or '') + '__facturae__' )
            f = open(fname_data_xml, 'wb')
            data_xml = data_xml.replace("&amp;", "Y")#Replace temp for process with xmlstartle
            f.write( data_xml )
            f.close()
            os.close(fileno_data_xml)
            all_paths = tools.config["addons_path"].split(",")
            for my_path in all_paths:
                if os.path.isdir(os.path.join(my_path, 'l10n_mx_facturae_base', 'SAT')):
                    # If dir is in path, save it on real_path
                    fname_scheme = my_path and os.path.join(my_path, 'l10n_mx_facturae_base', 'SAT', facturae_type + facturae_version +  '.' + scheme_type) or ''
                    #fname_scheme = os.path.join(tools.config["addons_path"], u'l10n_mx_facturae_base', u'SAT', facturae_type + facturae_version +  '.' + scheme_type )
                    fname_out = certificate_lib.b64str_to_tempfile(cr, uid, ids, base64.encodestring(''), file_suffix='.txt', file_prefix='openerp__' + (False or '') + '__schema_validation_result__' )
                    result = certificate_lib.check_xml_scheme(cr, uid, ids, fname_data_xml, fname_scheme, fname_out)
                    if result: #Valida el xml mediante el archivo xsd
                        raise osv.except_osv('Error al validar la estructura del xml!', 'Validación de XML versión %s:\n%s'%(facturae_version, result))
        return True

    def insert_pedimento(self, cr, uid, ids, context=None):
        date = datetime.now().strftime('%Y-%m-%d')
        invoice_line_obj = self.pool.get('account.invoice.line')
        stock_picking_out = self.pool.get('stock.picking.out')
        stock_move = self.pool.get('stock.move')
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.type == 'out_invoice':
                if rec.ignored_lot_ped == False:
                    origin = rec.origin
                    if origin:
                        if ":" in origin:
                            origin = tuple(origin.split(":"))
                        else:
                            origin = tuple([str(origin)])
                        sale_ids = self.pool.get('sale.order').search(cr, uid, [('name','in',(origin))])
                        if sale_ids:
                            stock_id = stock_picking_out.search(cr, uid, [('origin','in',(origin))])
                        else:
                            if rec.stock_picking_out:
                                stock_id = [rec.stock_picking_out.id]
                            else:
                                stock_id = stock_picking_out.search(cr, uid, [('name','in',(origin))])
                        
                        descriptions = [str(x.name) for x in rec.invoice_line if x.product_id.pediments_ids]
                        for line in rec.invoice_line:
                            # nodo = node.toxml()
                            #aduana="NOGALES, SONORA" fecha="2014-08-11" numero="123123123"
                            ### Este proceso se hace cuando tenemos el Alabaran Relacionado con la Venta
                            if stock_id:
                                pedimentos_line = []
                                product_id = line.product_id.id
                                if product_id:
                                    move_id = stock_move.search(cr, uid, [('picking_id','=',stock_id[0]),('product_id','=',product_id)])
                                    move_br = stock_move.browse(cr, uid, move_id, context=None)
                                    for move in move_br:
                                        if move.pedimento_id:
                                            xline = (0,0,{
                                                        'aduana': move.pedimento_id.pedimento_id.port_entrance,
                                                        'fecha': date,
                                                        'numero': move.pedimento_id.name,
                                                        })
                                            pedimentos_line.append(xline)
                                    pedimentos_line_not_repeat = []
                                    for a in pedimentos_line:
                                        if a not in pedimentos_line_not_repeat:
                                            pedimentos_line_not_repeat.append(a)
                                    # pedimentos_line = list(set(pedimentos_line))
                                    line.write({'pedimentos_manuales_ids': [x for x in pedimentos_line_not_repeat]})
                   
        return True  

    # def _get_facturae_invoice_xml_data(self, cr, uid, ids, context=None):
    #     xml_data = super(account_invoice, self)._get_facturae_invoice_xml_data(cr, uid, ids, context=context)
    #     for rec in self.browse(cr, uid, ids, context=None):
    #         # Esta Validacion va al Final que funcione el Modulo
    #         if rec.type == 'out_invoice':
    #             account_browse = self.browse(cr, uid, ids, context=None)
    #             pedimento_xml = self.insert_pedimento(cr, uid, ids, account_browse, xml_data, context=None)
    #             # addenda = addenda.replace('<cfdi>','').replace('</cfdi>','')
    #             # original =  ("</cfdi:Comprobante>").encode('utf8')
    #             # replacement = (addenda + "</cfdi:Comprobante>").encode('utf8')
    #             # xml_data_cadena = xml_data[1]
    #             if pedimento_xml:
    #                 xml_data_2 =(xml_data[0],pedimento_xml)
    #                 return xml_data_2
    #             else:
    #                 return xml_data
    #     return xml_data

    # def insert_pedimento(self, cr, uid, ids, account_browse, xml_data_attach, context=None):
    #     datas_fname = ""
    #     file_r = ""
    #     xml_data = ""
    #     date = datetime.now().strftime('%Y-%m-%d')
    #     account_browse = account_browse[0]
    #     invoice_line_obj = self.pool.get('account.invoice.line')
    #     stock_picking_out = self.pool.get('stock.picking.out')
    #     stock_move = self.pool.get('stock.move')
    #     xml_string = ""
    #     for rec in self.browse(cr, uid, ids, context=None):
    #         origin = rec.origin
            
    #         if origin:
    #             if ":" in origin:
    #                 origin = tuple(origin.split(":"))
    #             else:
    #                 origin = tuple([str(origin)])
    #             sale_ids = self.pool.get('sale.order').search(cr, uid, [('name','in',(origin))])
    #             if sale_ids:
    #                 stock_id = stock_picking_out.search(cr, uid, [('origin','in',(origin))])
    #             else:
    #                 if rec.stock_picking_out:
    #                     stock_id = rec.stock_picking_out.id
    #                 else:
    #                     stock_id = stock_picking_out.search(cr, uid, [('name','in',(origin))])
    #             try:
    #                 descriptions = [str(x.name) for x in rec.invoice_line if x.product_id.pediments_ids]
    #                 ####################### IMPORTANTE  ########################
    #                 ### Dispararla Cuando el Cliente Tenga Activado Addenda Honda
    #                 #############################################################
    #                 # attachment_xml_ids = self.pool.get('ir.attachment.facturae.mx').search(cr, uid, [('model_source','=','account.invoice'),('id_source','=',rec.id)], context=context)
    #                 # brow_rec = self.pool.get('ir.attachment.facturae.mx').browse(cr, uid, attachment_xml_ids[0])
    #                 # datas_fname = brow_rec.name
    #                 # xml_data = base64.decodestring(xml_data_attach[1])
    #                 dom = parseString(xml_data_attach)
    #                 root = dom.getElementsByTagNameNS('*', 'Comprobante')[0]
    #                 nodelines = root.getElementsByTagName('cfdi:Concepto')
    #                 for node in nodelines:
    #                     # nodo = node.toxml()
    #                     #aduana="NOGALES, SONORA" fecha="2014-08-11" numero="123123123"
    #                     description = node.attributes['descripcion'].value
    #                     if description in descriptions:
    #                         ### Este proceso se hace cuando tenemos el Alabaran Relacionado con la Venta
    #                         if stock_id:
    #                             pedimentos_line = []
    #                             line_id = invoice_line_obj.search(cr, uid, [('invoice_id','=',rec.id),('name','=',description)])
    #                             if line_id:
    #                                 line_br = invoice_line_obj.browse(cr, uid, line_id, context=None)[0]
    #                                 product_id = line_br.product_id.id
    #                                 move_id = stock_move.search(cr, uid, [('picking_id','=',stock_id[0]),('product_id','=',product_id)])
    #                                 move_br = stock_move.browse(cr, uid, move_id, context=None)
    #                                 for move in move_br:
    #                                     pedimento = dom.createElement('cfdi:InformacionAduanera ')
    #                                     pedimento.setAttribute('aduana',move.pedimento_id.pedimento_id.port_entrance)
    #                                     pedimento.setAttribute('fecha',date)
    #                                     pedimento.setAttribute('numero',move.pedimento_id.name)
    #                                     node.appendChild(pedimento)
    #                                     xline = (0,0,{
    #                                                 'aduana': move.pedimento_id.pedimento_id.port_entrance,
    #                                                 'fecha': date,
    #                                                 'numero': move.pedimento_id.name,
    #                                                 })
    #                                     pedimentos_line.append(xline)
    #                                 line_br.write({'pedimentos_manuales_ids': [x for x in pedimentos_line]})

    #                 data_xml = base64.encodestring(root.toxml('UTF-8'))
    #                 xml_string = base64.decodestring(data_xml)
    #             except:
    #                 return ""
    #         else:
    #             descriptions = [str(x.name) for x in rec.invoice_line]
    #             ####################### IMPORTANTE  ########################
    #             ### Dispararla Cuando el Cliente Tenga Activado Addenda Honda
    #             #############################################################
    #             # attachment_xml_ids = self.pool.get('ir.attachment.facturae.mx').search(cr, uid, [('model_source','=','account.invoice'),('id_source','=',rec.id)], context=context)
    #             # brow_rec = self.pool.get('ir.attachment.facturae.mx').browse(cr, uid, attachment_xml_ids[0])
    #             # datas_fname = brow_rec.name
    #             # xml_data = base64.decodestring(xml_data_attach[1])
    #             dom = parseString(xml_data_attach)
    #             root = dom.getElementsByTagNameNS('*', 'Comprobante')[0]
    #             nodelines = root.getElementsByTagName('cfdi:Concepto')
    #             for node in nodelines:
    #                 # nodo = node.toxml()
    #                 #aduana="NOGALES, SONORA" fecha="2014-08-11" numero="123123123"
    #                 description = node.attributes['descripcion'].value
    #                 if description in descriptions:
    #                     ### Este proceso se hace cuando tenemos el Alabaran Relacionado con la Venta
    #                     line_id = invoice_line_obj.search(cr, uid, [('invoice_id','=',rec.id),('name','=',description)])
    #                     line_br = invoice_line_obj.browse(cr, uid, line_id, context=None)[0]
    #                     product_id = line_br.product_id.id

    #                     if line_br.pedimentos_manuales_ids:
    #                         for pedbr in line_br.pedimentos_manuales_ids:
    #                             pedimento = dom.createElement('cfdi:InformacionAduanera ')
    #                             pedimento.setAttribute('aduana',pedbr.aduana)
    #                             pedimento.setAttribute('fecha',pedbr.fecha)
    #                             pedimento.setAttribute('numero',pedbr.numero)
    #                             node.appendChild(pedimento)
    #             data_xml = base64.encodestring(root.toxml('UTF-8'))
    #             xml_string = base64.decodestring(data_xml)
    #         #     data_xml = base64.encodestring(root.toxml('UTF-8'))
    #         #     xml_string = base64.decodestring(data_xml)
    #     return xml_string  
account_invoice()

class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit ='account.invoice.line'
    _columns = {
    'pediment_id': fields.many2one('stock.production.lot.pedimento','Pedimento'),
    'pediment_qty': fields.float('Cantidad Pedimento'),
    'lot_id': fields.many2one('stock.production.lot','No. de Serie'),
    'lot_qty': fields.float('Cantidad Pedimento'),
    'pedimentos_manuales_ids': fields.one2many('pedimento.manual.line', 'invoice_line_id','Pedimentos'),
        }

    _defaults = {
        }

account_invoice_line()

class pedimento_manual_line(osv.osv):
    _name = 'pedimento.manual.line'
    _description = 'Lineas Manuales para Pedimentos'
    _rec_name = 'aduana' 
    _columns = {
        'aduana':fields.char('Aduana/Puerto Entrada', size=128 ), 
        'fecha': fields.date('Fecha' ), 
        'numero':fields.char('No. Pedimento', size=64 ),
        'invoice_line_id': fields.many2one('account.invoice.line','ID Ref'),
    }
pedimento_manual_line()

class wizard_pedimento_manual(osv.osv_memory):
    _name = 'wizard.pedimento.manual'
    _description = 'Asistente Manual de Pedimento'
    _columns = {
        'wizard_pedimentos_ids': fields.one2many('wizard.pedimento.manual.line', 'wizard_id', 'Pedimentos'),
        'load_automatic': fields.boolean('Cargar Pedimentos'),
        'active_id': fields.integer('Active ID'),

    }

    def _get_active(self, cr, uid, context=None):
        active_id = 0
        if context:

            active_id = context.get('active_ids', [])[0]

        return active_id
    _defaults = {  
        'load_automatic': True,
        'active_id': _get_active,
        }

    def on_change_lines(self, cr, uid, ids, active_id, context=None):
        res = {}
        active_id = active_id
        account_line = self.pool.get('account.invoice.line')
        line_ids = []
        for rec in account_line.browse(cr, uid, [active_id], context=None):
            if rec.pedimentos_manuales_ids:
                for line in rec.pedimentos_manuales_ids:
                    xline = (0,0,{
                        'aduana': line.aduana,
                        'fecha':  line.fecha,
                        'numero': line.numero,
                        })
                    line_ids.append(xline)
                res.update({'wizard_pedimentos_ids':[x for x in line_ids]})
        return {'value':res}


    def assign_pedimentos(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            active_id = rec.active_id
            account_line = self.pool.get('account.invoice.line')
            line_ids = []

            for line in rec.wizard_pedimentos_ids:
                xline = (0,0,{
                        'aduana': line.aduana,
                        'fecha':  line.fecha,
                        'numero': line.numero,
                        })
                line_ids.append(xline)
            for account in account_line.browse(cr, uid, [active_id], context=None):
                for pedimento in account.pedimentos_manuales_ids:
                    pedimento.unlink()
                account.write({'pedimentos_manuales_ids':[x for x in line_ids]})
        return True

wizard_pedimento_manual()

class wizard_pedimento_manual_line(osv.osv_memory):
    _name = 'wizard.pedimento.manual.line'
    _description = 'Asistente Lineas Manuales para Pedimentos'
    _rec_name = 'aduana' 
    _columns = {
        'aduana':fields.char('Aduana/Puerto Entrada', size=128, required=True), 
        'fecha': fields.date('Fecha', required=True), 
        'numero':fields.char('No. Pedimento', size=64 ,required=True),
        'wizard_id': fields.many2one('wizard.pedimento.manual','ID Ref'),
    }
    _defaults = {  
        'fecha': datetime.now().strftime('%Y-%m-%d'), 
        }
wizard_pedimento_manual_line()

