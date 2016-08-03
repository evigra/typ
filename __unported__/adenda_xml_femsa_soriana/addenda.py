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

from openerp.osv import osv, fields
import time
from datetime import datetime, date
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import base64
from openerp import SUPERUSER_ID, _

from xml.dom import minidom
from xml.dom.minidom import Document , parse , parseString

### ADENDA FEMSA
class addenda_honda_wizard_femsa(osv.osv_memory):
    _name = "addenda.honda.wizard.femsa"
    _description = "Wizard Addenda de Honda"
    _columns = {
    'date': fields.date('Fecha Consulta'),
    #'ref': fields.char('Nombre del CSV', size=256, required=True),
    'invoice_id': fields.many2one('account.invoice', 'Factura', required=True),

    ### ESTOS SE VAN A USAR PARA GENERAR LA ADENDA PARA DESCARGA
    'datas_fname': fields.char('File Name',size=256),
    'file': fields.binary('Addenda'),
    'download_file': fields.boolean('Descargar Archivo'),
    }

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        'download_file': False,
        }

    def get_info(self, cr, uid, ids, context=None):
        ## Primero para comenzar eliminar lo que tenga el modelo addenda_honda_file
        # cr.execute("""
        #        delete from addenda_honda_file ;
        #                 """)

        datas_fname = ""
        file_r = ""
        xml_data = ""
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.download_file == False:
                account_browse = self.pool.get('account.invoice').browse(cr, uid, rec.invoice_id.id, context=None)
                if account_browse.partner_id.addenda_femsa:
                    if account_browse.type in ('out_invoice','out_refund'):
                        clase_doc = '1' if account_browse.type == 'out_invoice' else '9'
                        attachment_xml_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',account_browse.id),('name','like','.xml')], context=context)
                        brow_rec = self.pool.get('ir.attachment').browse(cr, uid, attachment_xml_ids[0])

                        if attachment_xml_ids:
                            ####################### IMPORTANTE  ########################
                            ### Dispararla Cuando el Cliente Tenga Activado Addenda Honda
                            #############################################################
                            datas_fname = brow_rec.name
                            xml_data = base64.decodestring(brow_rec.datas)
                            ##print xml_data
                            dom = parseString(xml_data)
                            root = dom.getElementsByTagNameNS('*', 'Comprobante')[0]
                            #nodelines = root.getElementsByTagName('cfdi:Conceptos')
                            addenda = dom.getElementsByTagName('cfdi:Addenda')[0] # creas el elemento addenda
                            ### CREANDO MI PROPIA TAG DENTRO DE LA ADENDA
                            ## GPC:HondaPartes xmlns:GPC="http://www.honda.net.mx/GPC" tipoDocumento="GPC" tipoComprobante="FACTURA" moneda="USD" fecha="20140619" folio="H698" unidadDeNegocio="HCL" asn="06007473"

                            femsa = dom.createElement('Documento')
                            addenda.appendChild(femsa)

                            factura_femsa = dom.createElement('FacturaFemsa')
                            femsa.appendChild(factura_femsa)

                            ### DETALLE DE LA ADENDA ###
                            noVersAdd = dom.createElement('noVersAdd')
                            factura_femsa.appendChild(noVersAdd)
                            text = dom.createTextNode('1')
                            noVersAdd.appendChild(text)

                            claseDoc = dom.createElement('claseDoc')
                            factura_femsa.appendChild(claseDoc)
                            text = dom.createTextNode(clase_doc)
                            claseDoc.appendChild(text)

                            noSociedad = dom.createElement('noSociedad')
                            factura_femsa.appendChild(noSociedad)
                            if account_browse.no_sociedad:
                                text = dom.createTextNode(account_browse.no_sociedad)
                                noSociedad.appendChild(text)

                            noProveedor = dom.createElement('noProveedor')
                            factura_femsa.appendChild(noProveedor)
                            text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
                            noProveedor.appendChild(text)

                            noPedido = dom.createElement('noPedido')
                            factura_femsa.appendChild(noPedido)
                            if account_browse.no_pedido_femsa:
                                text = dom.createTextNode(account_browse.no_pedido_femsa)
                                noPedido.appendChild(text)

                            moneda = dom.createElement('moneda')
                            factura_femsa.appendChild(moneda)
                            text = dom.createTextNode(account_browse.currency_id.name)
                            moneda.appendChild(text)

                            noEntrada = dom.createElement('noEntrada')
                            factura_femsa.appendChild(noEntrada)
                            if account_browse.no_entrada_femsa:
                                text = dom.createTextNode(account_browse.no_entrada_femsa)
                                noEntrada.appendChild(text)

                            noRemision = dom.createElement('noRemision')
                            factura_femsa.appendChild(noRemision)
                            if account_browse.no_remision_femsa:
                                text = dom.createTextNode(account_browse.no_remision_femsa)
                                noRemision.appendChild(text)

                            noSocio = dom.createElement('noSocio')
                            factura_femsa.appendChild(noSocio)
                            if account_browse.no_socio_femsa:
                                text = dom.createTextNode(account_browse.no_socio_femsa)
                                noSocio.appendChild(text)

                            centroCostos = dom.createElement('centroCostos')
                            factura_femsa.appendChild(centroCostos)
                            if account_browse.centro_costos:
                                text = dom.createTextNode(account_browse.centro_costos)
                                centroCostos.appendChild(text)

                            iniPerLiq = dom.createElement('iniPerLiq')
                            factura_femsa.appendChild(iniPerLiq)
                            if account_browse.inicio_liquidacion:
                                text = dom.createTextNode(account_browse.inicio_liquidacion)
                                iniPerLiq.appendChild(text)

                            finPerLiq = dom.createElement('finPerLiq')
                            factura_femsa.appendChild(finPerLiq)
                            if account_browse.fin_liquidacion:
                                text = dom.createTextNode(account_browse.fin_liquidacion)
                                finPerLiq.appendChild(text)

                            retencion1 = dom.createElement('retencion1')
                            factura_femsa.appendChild(retencion1)
                            if account_browse.retencion1:
                                text = dom.createTextNode(account_browse.retencion1)
                                retencion1.appendChild(text)

                            retencion2 = dom.createElement('retencion2')
                            factura_femsa.appendChild(retencion2)
                            if account_browse.retencion2:
                                text = dom.createTextNode(account_browse.retencion2)
                                retencion2.appendChild(text)

                            retencion3 = dom.createElement('retencion3')
                            factura_femsa.appendChild(retencion3)
                            if account_browse.retencion3:
                                text = dom.createTextNode(account_browse.retencion3)
                                retencion3.appendChild(text)

                            email = dom.createElement('email')
                            factura_femsa.appendChild(email)
                            if account_browse.company_id.email:
                                text = dom.createTextNode(account_browse.company_id.email or '')
                                email.appendChild(text)


                            file_r = brow_rec.datas
                            ### EL  root.getElementsByTagNames('*','Comprbante') Extrae la cadena y la convierte a UTF8
                        rec.write({'datas_fname':datas_fname,'file':base64.encodestring(root.toxml('UTF-8')),'download_file': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'addenda.honda.wizard.femsa',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }

addenda_honda_wizard_femsa()

######### ADENDA SORIANA
class addenda_honda_wizard_soriana(osv.osv_memory):
    _name = "addenda.honda.wizard.soriana"
    _description = "Wizard Addenda de Honda"
    _columns = {
    'date': fields.date('Fecha Consulta'),
    #'ref': fields.char('Nombre del CSV', size=256, required=True),
    'invoice_id': fields.many2one('account.invoice', 'Factura', required=True),

    ### ESTOS SE VAN A USAR PARA GENERAR LA ADENDA PARA DESCARGA
    'datas_fname': fields.char('File Name',size=256),
    'file': fields.binary('Addenda'),
    'download_file': fields.boolean('Descargar Archivo'),
    }

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        'download_file': False,
        }

    def get_info(self, cr, uid, ids, context=None):
        ## Primero para comenzar eliminar lo que tenga el modelo addenda_honda_file
        # cr.execute("""
        #        delete from addenda_honda_file ;
        #                 """)

        datas_fname = ""
        file_r = ""
        xml_data = ""
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.download_file == False:
                account_browse = self.pool.get('account.invoice').browse(cr, uid, rec.invoice_id.id, context=None)
                if account_browse.partner_id.addenda_soriana:
                    if account_browse.type in ('out_invoice','out_refund'):
                        clase_doc = '1' if account_browse.type == 'out_invoice' else '9'
                        attachment_xml_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',account_browse.id),('name','like','.xml')], context=context)
                        brow_rec = self.pool.get('ir.attachment').browse(cr, uid, attachment_xml_ids[0])

                        if attachment_xml_ids:
                            ####################### IMPORTANTE  ########################
                            ### Dispararla Cuando el Cliente Tenga Activado Addenda Honda
                            #############################################################
                            datas_fname = brow_rec.name
                            xml_data = base64.decodestring(brow_rec.datas)
                            ##print xml_data
                            dom = parseString(xml_data)
                            root = dom.getElementsByTagNameNS('*', 'Comprobante')[0]
                            #nodelines = root.getElementsByTagName('cfdi:Conceptos')
                            addenda = dom.getElementsByTagName('cfdi:Addenda')[0] # creas el elemento addenda
                            ### CREANDO MI PROPIA TAG DENTRO DE LA ADENDA
                            ## GPC:HondaPartes xmlns:GPC="http://www.honda.net.mx/GPC" tipoDocumento="GPC" tipoComprobante="FACTURA" moneda="USD" fecha="20140619" folio="H698" unidadDeNegocio="HCL" asn="06007473"

                            soriana = dom.createElement('DSCargaRemisionProv')
                            addenda.appendChild(soriana)

                            remision = dom.createElement('Remision')
                            soriana.appendChild(remision)

                            remision.setAttribute('Id',"1")
                            remision.setAttribute('RowOrder',"1")

                            Proveedor = dom.createElement('Proveedor')
                            remision.appendChild(Proveedor)
                            text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
                            Proveedor.appendChild(text)

                            ##### REMISION #######
                            serie_factura = ""
                            sequence_obj = self.pool.get('ir.sequence')
                            invoice_id__sequence_id = account_browse._get_invoice_sequence()

                            sequence_id = invoice_id__sequence_id[account_browse.id]
                            sequence = False
                            if sequence_id:
                                sequence = sequence_obj.browse(
                                    cr, uid, [sequence_id], context)[0]
                            serie_factura = sequence.approval_id.serie or ''

                            Remision= dom.createElement('Remision')
                            remision.appendChild(Remision)
                            if account_browse.number:
                                text = dom.createTextNode(serie_factura+'-'+account_browse.number)
                                Remision.appendChild(text)

                            Consecutivo= dom.createElement('Consecutivo')
                            remision.appendChild(Consecutivo)
                            text = dom.createTextNode('0')
                            Consecutivo.appendChild(text)

                            FechaRemision= dom.createElement('FechaRemision')
                            remision.appendChild(FechaRemision)
                            text = dom.createTextNode(str(account_browse.date_invoice)+"T00:00:00")
                            FechaRemision.appendChild(text)

                            Tienda= dom.createElement('Tienda')
                            remision.appendChild(Tienda)
                            text = dom.createTextNode(account_browse.tienda_entrega_soriana)
                            Tienda.appendChild(text)

                            TipoMoneda= dom.createElement('TipoMoneda')
                            remision.appendChild(TipoMoneda)
                            moneda = account_browse.currency_id.name.upper()

                            if moneda == 'MXN':
                                text = dom.createTextNode('1')
                            elif moneda == 'USD':
                                text = dom.createTextNode('2')
                            else:
                                text = dom.createTextNode('3')
                            TipoMoneda.appendChild(text)

                            TipoBulto= dom.createElement('TipoBulto')
                            remision.appendChild(TipoBulto)
                            text = dom.createTextNode(account_browse.tipo_bulto)
                            TipoBulto.appendChild(text)

                            EntregaMercancia= dom.createElement('EntregaMercancia')
                            remision.appendChild(EntregaMercancia)
                            if account_browse.entrega_mercancia != 'otro':
                                text = dom.createTextNode(account_browse.entrega_mercancia)
                                EntregaMercancia.appendChild(text)
                            else:
                                text = dom.createTextNode(account_browse.entrega_mercancia_especifica)
                                EntregaMercancia.appendChild(text)

                            CumpleReqFiscales= dom.createElement('CumpleReqFiscales')
                            remision.appendChild(CumpleReqFiscales)
                            text = dom.createTextNode('true')
                            CumpleReqFiscales.appendChild(text)

                            CantidadBultos= dom.createElement('CantidadBultos')
                            remision.appendChild(CantidadBultos)
                            cantidad_bultos = 0
                            for linea in account_browse.invoice_line:
                                cantidad_bultos+= linea.quantity
                            text = dom.createTextNode(str(int(cantidad_bultos)))
                            CantidadBultos.appendChild(text)

                            Subtotal= dom.createElement('Subtotal')
                            remision.appendChild(Subtotal)
                            text = dom.createTextNode(str(account_browse.amount_untaxed))
                            Subtotal.appendChild(text)

                            Descuentos= dom.createElement('Descuentos')
                            remision.appendChild(Descuentos)
                            text = dom.createTextNode('0')
                            Descuentos.appendChild(text)

                            ieps_amount = 0.0
                            iva_amount = 0.0
                            otros_impuestos = 0.0

                            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
                            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
                            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
                            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
                            for impuesto in account_browse.tax_line:
                                if 'IVA' in impuesto.name.upper():
                                    iva_amount = impuesto.amount
                                elif 'IEPS' in impuesto.name.upper():
                                    ieps_amount = impuesto.amount
                                else:
                                    otros_impuestos+= impuesto.amount

                            IEPS= dom.createElement('IEPS')
                            remision.appendChild(IEPS)
                            text = dom.createTextNode(str(ieps_amount))
                            IEPS.appendChild(text)

                            IVA= dom.createElement('IVA')
                            remision.appendChild(IVA)
                            text = dom.createTextNode(str(iva_amount))
                            IVA.appendChild(text)

                            OtrosImpuestos= dom.createElement('OtrosImpuestos')
                            remision.appendChild(OtrosImpuestos)
                            text = dom.createTextNode(str(otros_impuestos))
                            OtrosImpuestos.appendChild(text)

                            Total= dom.createElement('Total')
                            remision.appendChild(Total)
                            text = dom.createTextNode(str(account_browse.amount_total))
                            Total.appendChild(text)

                            CantidadPedidos= dom.createElement('CantidadPedidos')
                            remision.appendChild(CantidadPedidos)
                            text = dom.createTextNode(str(account_browse.cantidad_pedidos))
                            CantidadPedidos.appendChild(text)

                            FechaEntregaMercancia= dom.createElement('FechaEntregaMercancia')
                            remision.appendChild(FechaEntregaMercancia)
                            if account_browse.fecha_entrega_soriana:
                                text = dom.createTextNode(str(account_browse.fecha_entrega_soriana)+"T00:00:00")
                                FechaEntregaMercancia.appendChild(text)

                            FolioNotaEntrada= dom.createElement('FolioNotaEntrada')
                            remision.appendChild(FolioNotaEntrada)
                            if account_browse.folio_entrada_soriana:
                                text = dom.createTextNode(account_browse.folio_entrada_soriana)
                                FolioNotaEntrada.appendChild(text)

                            ##### Pedidos #####
                            pedidos = dom.createElement('Pedidos')
                            soriana.appendChild(pedidos)

                            pedidos.setAttribute('Id',"1")
                            pedidos.setAttribute('RowOrder',"1")

                            Proveedor = dom.createElement('Proveedor')
                            pedidos.appendChild(Proveedor)
                            text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
                            Proveedor.appendChild(text)

                            Remision = dom.createElement('Remision')
                            pedidos.appendChild(Remision)
                            text = dom.createTextNode(serie_factura+'-'+account_browse.number)
                            Remision.appendChild(text)

                            FolioPedido = dom.createElement('FolioPedido')
                            pedidos.appendChild(FolioPedido)
                            text = dom.createTextNode(account_browse.no_pedido_soriana)
                            FolioPedido.appendChild(text)

                            Tienda = dom.createElement('Tienda')
                            pedidos.appendChild(Tienda)
                            text = dom.createTextNode(account_browse.tienda_entrega_soriana)
                            Tienda.appendChild(text)

                            CantidadArticulos = dom.createElement('CantidadArticulos')
                            pedidos.appendChild(CantidadArticulos)
                            cr.execute("select sum(quantity) from account_invoice_line where invoice_id=%s" % account_browse.id)
                            cantidad_articulos = cr.fetchall()
                            if  cantidad_articulos[0]:
                                cantidad_articulos = cantidad_articulos[0][0]
                            text = dom.createTextNode(str(int(cantidad_articulos)))
                            CantidadArticulos.appendChild(text)

                            ###### ARTICULOS ######
                            i=1
                            for line in account_browse.invoice_line:
                                articulos = dom.createElement('Articulos')
                                soriana.appendChild(articulos)

                                articulos.setAttribute('Id',"Articulos1")
                                articulos.setAttribute('RowOrder',str(i))

                                Proveedor = dom.createElement('Proveedor')
                                articulos.appendChild(Proveedor)
                                text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
                                Proveedor.appendChild(text)

                                Remision = dom.createElement('Remision')
                                articulos.appendChild(Remision)
                                text = dom.createTextNode(serie_factura+'-'+account_browse.number)
                                Remision.appendChild(text)

                                FolioPedido = dom.createElement('FolioPedido')
                                articulos.appendChild(FolioPedido)
                                text = dom.createTextNode(account_browse.no_pedido_soriana)
                                FolioPedido.appendChild(text)

                                Tienda = dom.createElement('Tienda')
                                articulos.appendChild(Tienda)
                                text = dom.createTextNode(account_browse.tienda_entrega_soriana)
                                Tienda.appendChild(text)

                                Codigo = dom.createElement('Codigo')
                                articulos.appendChild(Codigo)
                                if line.codigo_soriana:
                                    text = dom.createTextNode(line.codigo_soriana)
                                    Codigo.appendChild(text)

                                CantidadUnidadCompra = dom.createElement('CantidadUnidadCompra')
                                articulos.appendChild(CantidadUnidadCompra)
                                text = dom.createTextNode(str(int(line.quantity)))
                                CantidadUnidadCompra.appendChild(text)

                                CostoNetoUnidadCompra = dom.createElement('CostoNetoUnidadCompra')
                                articulos.appendChild(CostoNetoUnidadCompra)
                                text = dom.createTextNode(str(line.price_subtotal))
                                CostoNetoUnidadCompra.appendChild(text)

                                amount_ieps = 0.0
                                amount_iva = 0.0
                                subtotal_line = line.price_subtotal
                                for tax in line.invoice_line_tax_id:
                                    if 'IEPS' in tax.name.upper():
                                        if tax.type == 'percent':
                                            amount_ieps = tax.amount * 100
                                        else:
                                            amount_ieps = tax.amount
                                    elif 'IVA' in tax.name.upper():
                                        if tax.type == 'percent':
                                            amount_iva = tax.amount * 100
                                        else:
                                            amount_ieps = tax.amount

                                PorcentajeIEPS = dom.createElement('PorcentajeIEPS')
                                articulos.appendChild(PorcentajeIEPS)
                                text = dom.createTextNode(str("%.2f" % amount_ieps))
                                PorcentajeIEPS.appendChild(text)

                                PorcentajeIVA = dom.createElement('PorcentajeIVA')
                                articulos.appendChild(PorcentajeIVA)
                                text = dom.createTextNode(str("%.2f" % amount_iva))
                                PorcentajeIVA.appendChild(text)

                                i+=1

                            file_r = brow_rec.datas
                        rec.write({'datas_fname':datas_fname,'file':base64.encodestring(root.toxml('UTF-8')),'download_file': True})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'addenda.honda.wizard.soriana',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }

addenda_honda_wizard_soriana()


class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'
    _columns = {
    'codigo_soriana': fields.char('Codigo Soriana', size=64),
    }
account_invoice_line()


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = 'account.invoice'
    _columns = {
    ####### ADENDA MANUAL ##########
    'addenda_manual': fields.boolean('Addenda Manual', help='Este Campo Permite Insertar una Addenda Manualmente y esta sera insertada al XML'),
    'addenda_xml': fields.text('Fragmento de la Addenda', help='<cfdi:Addenda> Texto </cfdi:Addenda>', ),
    ####### ADENDA FEMSA ##########
    'no_sociedad': fields.char('No. de Sociedad', size=128, help='Capturar el No. de Sociedad para los Clientes FEMSA'),
    'no_pedido_femsa': fields.char('No. de Pedido', size=128, help='Capturar el No. de Pedido asignado por los Clientes FEMSA'),
    'no_entrada_femsa': fields.char('No. de Entrada', size=128, help='Capturar el No. de Entrada asignado por los Clientes FEMSA'),
    'no_remision_femsa': fields.char('No. de Remision', size=128, help='Capturar el No. de Remision asignado por los Clientes FEMSA'),
    'no_socio_femsa': fields.char('No. de Socio', size=128, help='Capturar el No. de Socio asignado por los Clientes FEMSA'),
    'centro_costos': fields.char('Centro de Costos', size=128, help='Capturar el No. Centro de Costos FEMSA'),
    'customer_femsa': fields.boolean('Cliente FEMSA', help='Este Campoo Funciona para la Creacion de la Addenda Tomando y pidiendo Campos Especificos para Este Cliente', ),
    'inicio_liquidacion': fields.date('Inicio de Liquidacion', help='Fecha de Inicio de Liquidacion'),
    'fin_liquidacion': fields.date('Fin de Liquidacion', help='Fecha de Fin de Liquidacion'),
    'retencion1': fields.char('Retencion 01', size=128),
    'retencion2': fields.char('Retencion 02', size=128),
    'retencion3': fields.char('Retencion 03', size=128),

    ###### ADENDA SORIANA ########
    'customer_soriana': fields.boolean('Cliente SORIANA', help='Este Campoo Funciona para la Creacion de la Addenda Tomando y pidiendo Campos Especificos para Este Cliente'),
    'no_remision_soriana': fields.char('No. de Remision', size=128, help='Capturar el No. de Remision para los Clientes de Soriana'),
    'fecha_remision_soriana': fields.date('Fecha de Remision', help='Fecha de Remision del Cliente'),
    'tienda_entrega_soriana': fields.char('Tienda Entrega', size=128, help='Capturar el No. de Tienda para la Entrega de Mercancia'),
    'tipo_bulto': fields.selection([('1','CAJAS'),('2','BOLSAS')],'Tipo Bulto', help='Define como Se esta Enviando la Mercancia para el Cliente', ),
    'entrega_mercancia': fields.selection([('1','DIRECTO TIENDA'),
('2','509 - CEDIS MEXICO'),
('3','598 - CEDIS SALINAS'),
('5','578 - CEDIS QUERETARO'),
('11','583 - PERECEDEROS'),
('12','530 - CEDIS PERECEDEROS MONTERREY'),
('13','521 - CEDIS PERECEDEROS VILLAHERMOSA'),
('14','561 - CEDIS LAREDO'),
('15','562 - CEDIS JUAREZ'),
('16','568 - CEDIS LA PAZ'),
('17','526 - CEDIS NOGALES'),
('18','560 - CEDIS ARMADO DE DESPENSAS'),
('19','531 - CEDIS PERECEDEROS SIP MEXICO'),
('20','532 - CEDIS PERECEDEROS SIP HERMOSILLO'),
('21','533 - CEDIS PERECEDEROS CHIHUAHUA'),
('22','527 - MAQUILAS Y DETALLISTAS'),
('23','528 - CONFECCIONES Y MAQUILAS H.M.'),
('24','5513 - CD MÉXICO'),
('otro','Otro'),
],'Entrega Mercancia', help='Define en que Tienda se Entregara la Mercancia', ),
    'entrega_mercancia_especifica': fields.char('Especifica', size=128, help='Capturar el No. de tienda para Entregar la Mercancia al Cliente Soriana'),

    'cantidad_bultos': fields.integer('Cantidad de Bultos'),
    'cantidad_pedidos': fields.integer('Cantidad de Pedidos'),
    'fecha_entrega_soriana': fields.date('Fecha de Entrega', help='Fecha de Entrega de la Mercancia'),
    'no_pedido_soriana': fields.char('No. de Pedido', size=128, help='Capturar el No. de Pedido asignado por los Clientes Soriana'),
    'folio_entrada_soriana': fields.char('Folio Nota entrada', size=128, help='Capturar el No. de Remision para Refacturacion'),

    }

    _defaults = {
        'tipo_bulto': '1',
        'entrega_mercancia': '1',
        'cantidad_pedidos': 1,
        }
    # def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
    #         date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
    #     if not partner_id:
    #         return {'value':{}}
    #     result =  super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,\
    #         date_invoice, payment_term, partner_bank_id, company_id)
    #     partner_br = self.pool.get('res.partner').browse(cr, uid, partner_id, context=None)
    #     if partner_br.addenda_femsa:
    #         result['value'].update({'customer_femsa':True})
    #     if partner_br.addenda_soriana:
    #         result['value'].update({'customer_soriana':True})
    #     return result


    def _get_facturae_invoice_xml_data(self, cr, uid, ids, context=None):
        xml_data = super(account_invoice, self)._get_facturae_invoice_xml_data(cr, uid, ids, context=context)
        for rec in self.browse(cr, uid, ids, context=None):
            # Esta Validacion va al Final que funcione el Modulo
            if rec.type == 'out_invoice':
                if rec.addenda_manual:

                    account_browse = self.browse(cr, uid, ids, context=None)
                    addenda = rec.addenda_xml
                    original =  ("</cfdi:Comprobante>").encode('utf8')
                    replacement = (addenda + "</cfdi:Comprobante>").encode('utf8')
                    xml_data_cadena = xml_data[1]
                    xml_data_2 =(xml_data[0],xml_data_cadena.replace(original, replacement))
                    return xml_data_2
                elif rec.customer_soriana:
                    account_browse = self.browse(cr, uid, ids, context=None)
                    addenda = self.insert_addenda_soriana(cr, uid, ids, context=None)
                    addenda = addenda.replace('<cfdi>','').replace('</cfdi>','')
                    original =  ("</cfdi:Comprobante>").encode('utf8')
                    replacement = (addenda + "</cfdi:Comprobante>").encode('utf8')
                    xml_data_cadena = xml_data[1]
                    xml_data_2 =(xml_data[0],xml_data_cadena.replace(original, replacement))
                    return xml_data_2
                elif rec.customer_femsa:
                    account_browse = self.browse(cr, uid, ids, context=None)
                    addenda = self.insert_addenda_femsa(cr, uid, ids, context=None)
                    addenda = addenda.replace('<cfdi>','').replace('</cfdi>','')
                    original =  ("</cfdi:Comprobante>").encode('utf8')
                    replacement = (addenda + "</cfdi:Comprobante>").encode('utf8')
                    xml_data_cadena = xml_data[1]
                    xml_data_2 =(xml_data[0],xml_data_cadena.replace(original, replacement))
                    return xml_data_2
        return xml_data


    def insert_addenda_femsa(self, cr, uid, ids, context=None):

        datas_fname = ""
        file_r = ""
        xml_data = ""
        date = datetime.now().strftime('%Y-%m-%d')
        for rec in self.browse(cr, uid, ids, context=None):
            account_browse = rec
            serie_factura = ""
            sequence_obj = self.pool.get('ir.sequence')
            invoice_id__sequence_id = self._get_invoice_sequence(cr, uid, ids, context=context)

            sequence_id = invoice_id__sequence_id[rec.id]
            sequence = False
            if sequence_id:
                sequence = sequence_obj.browse(
                    cr, uid, [sequence_id], context)[0]
            serie_factura = sequence.approval_id.serie or ''

            clase_doc = '1' if account_browse.type == 'out_invoice' else '9'

            ####################### IMPORTANTE  ########################
            dom = parseString("<cfdi></cfdi>")
            root = dom.getElementsByTagNameNS('*', 'cfdi')[0]
            #nodelines = root.getElementsByTagName('cfdi:Conceptos')
            addenda = dom.createElement('cfdi:Addenda') # creas el elemento addenda
            root.appendChild(addenda)

            femsa = dom.createElement('Documento')
            addenda.appendChild(femsa)

            factura_femsa = dom.createElement('FacturaFemsa')
            femsa.appendChild(factura_femsa)

            ### DETALLE DE LA ADENDA ###
            noVersAdd = dom.createElement('noVersAdd')
            factura_femsa.appendChild(noVersAdd)
            text = dom.createTextNode('1')
            noVersAdd.appendChild(text)

            claseDoc = dom.createElement('claseDoc')
            factura_femsa.appendChild(claseDoc)
            text = dom.createTextNode(clase_doc)
            claseDoc.appendChild(text)

            noSociedad = dom.createElement('noSociedad')
            factura_femsa.appendChild(noSociedad)
            text = dom.createTextNode(account_browse.no_sociedad)
            noSociedad.appendChild(text)

            noProveedor = dom.createElement('noProveedor')
            factura_femsa.appendChild(noProveedor)
            text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
            noProveedor.appendChild(text)

            noPedido = dom.createElement('noPedido')
            factura_femsa.appendChild(noPedido)
            text = dom.createTextNode(account_browse.no_pedido_femsa)
            noPedido.appendChild(text)

            moneda = dom.createElement('moneda')
            factura_femsa.appendChild(moneda)
            text = dom.createTextNode(account_browse.currency_id.name)
            moneda.appendChild(text)

            noEntrada = dom.createElement('noEntrada')
            factura_femsa.appendChild(noEntrada)
            text = dom.createTextNode(account_browse.no_entrada_femsa)
            noEntrada.appendChild(text)

            noRemision = dom.createElement('noRemision')
            factura_femsa.appendChild(noRemision)
            text = dom.createTextNode(account_browse.no_remision_femsa)
            noRemision.appendChild(text)

            noSocio = dom.createElement('noSocio')
            factura_femsa.appendChild(noSocio)
            if account_browse.no_socio_femsa:
                text = dom.createTextNode(account_browse.no_socio_femsa)
                noSocio.appendChild(text)

            centroCostos = dom.createElement('centroCostos')
            factura_femsa.appendChild(centroCostos)
            if account_browse.centro_costos:
                text = dom.createTextNode(account_browse.centro_costos)
                centroCostos.appendChild(text)

            iniPerLiq = dom.createElement('iniPerLiq')
            factura_femsa.appendChild(iniPerLiq)
            if account_browse.inicio_liquidacion:
                text = dom.createTextNode(account_browse.inicio_liquidacion)
                iniPerLiq.appendChild(text)

            finPerLiq = dom.createElement('finPerLiq')
            factura_femsa.appendChild(finPerLiq)
            if account_browse.fin_liquidacion:
                text = dom.createTextNode(account_browse.fin_liquidacion)
                finPerLiq.appendChild(text)

            retencion1 = dom.createElement('retencion1')
            factura_femsa.appendChild(retencion1)
            if account_browse.retencion1:
                text = dom.createTextNode(account_browse.retencion1)
                retencion1.appendChild(text)

            retencion2 = dom.createElement('retencion2')
            factura_femsa.appendChild(retencion2)
            if account_browse.retencion2:
                text = dom.createTextNode(account_browse.retencion2)
                retencion2.appendChild(text)

            retencion3 = dom.createElement('retencion3')
            factura_femsa.appendChild(retencion3)
            if account_browse.retencion3:
                text = dom.createTextNode(account_browse.retencion3)
                retencion3.appendChild(text)

            email = dom.createElement('email')
            factura_femsa.appendChild(email)
            if account_browse.company_id.email:
                text = dom.createTextNode(account_browse.company_id.email or '')
                email.appendChild(text)

            data_xml = base64.encodestring(root.toxml('UTF-8'))
            xml_string = base64.decodestring(data_xml)
        return xml_string

    def insert_addenda_soriana(self, cr, uid, ids, context=None):

        datas_fname = ""
        file_r = ""
        xml_data = ""
        date = datetime.now().strftime('%Y-%m-%d')
        for rec in self.browse(cr, uid, ids, context=None):
            account_browse = rec
            serie_factura = ""
            sequence_obj = self.pool.get('ir.sequence')
            invoice_id__sequence_id = self._get_invoice_sequence(cr, uid, ids, context=context)

            sequence_id = invoice_id__sequence_id[rec.id]
            sequence = False
            if sequence_id:
                sequence = sequence_obj.browse(
                    cr, uid, [sequence_id], context)[0]
            serie_factura = sequence.approval_id.serie or ''


            ####################### IMPORTANTE  ########################
            dom = parseString("<cfdi></cfdi>")
            root = dom.getElementsByTagNameNS('*', 'cfdi')[0]
            #nodelines = root.getElementsByTagName('cfdi:Conceptos')
            addenda = dom.createElement('cfdi:Addenda') # creas el elemento addenda
            root.appendChild(addenda)

            soriana = dom.createElement('DSCargaRemisionProv')
            addenda.appendChild(soriana)

            remision = dom.createElement('Remision')
            soriana.appendChild(remision)

            remision.setAttribute('Id',"1")
            remision.setAttribute('RowOrder',"1")

            Proveedor = dom.createElement('Proveedor')
            remision.appendChild(Proveedor)
            text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
            Proveedor.appendChild(text)

            ##### REMISION #######

            Remision= dom.createElement('Remision')
            remision.appendChild(Remision)
            if account_browse.number:
                text = dom.createTextNode(serie_factura+'-'+account_browse.number)
                Remision.appendChild(text)

            Consecutivo= dom.createElement('Consecutivo')
            remision.appendChild(Consecutivo)
            text = dom.createTextNode('0')
            Consecutivo.appendChild(text)

            FechaRemision= dom.createElement('FechaRemision')
            remision.appendChild(FechaRemision)
            text = dom.createTextNode(str(account_browse.date_invoice)+"T00:00:00")
            FechaRemision.appendChild(text)

            Tienda= dom.createElement('Tienda')
            remision.appendChild(Tienda)
            text = dom.createTextNode(account_browse.tienda_entrega_soriana)
            Tienda.appendChild(text)

            TipoMoneda= dom.createElement('TipoMoneda')
            remision.appendChild(TipoMoneda)
            moneda = account_browse.currency_id.name.upper()

            if moneda == 'MXN':
                text = dom.createTextNode('1')
            elif moneda == 'USD':
                text = dom.createTextNode('2')
            else:
                text = dom.createTextNode('3')
            TipoMoneda.appendChild(text)

            TipoBulto= dom.createElement('TipoBulto')
            remision.appendChild(TipoBulto)
            text = dom.createTextNode(account_browse.tipo_bulto)
            TipoBulto.appendChild(text)

            EntregaMercancia= dom.createElement('EntregaMercancia')
            remision.appendChild(EntregaMercancia)
            if account_browse.entrega_mercancia != 'otro':
                text = dom.createTextNode(account_browse.entrega_mercancia)
                EntregaMercancia.appendChild(text)
            else:
                text = dom.createTextNode(account_browse.entrega_mercancia_especifica)
                EntregaMercancia.appendChild(text)

            CumpleReqFiscales= dom.createElement('CumpleReqFiscales')
            remision.appendChild(CumpleReqFiscales)
            text = dom.createTextNode('true')
            CumpleReqFiscales.appendChild(text)

            CantidadBultos= dom.createElement('CantidadBultos')
            remision.appendChild(CantidadBultos)
            cantidad_bultos = 0
            for linea in account_browse.invoice_line:
                cantidad_bultos+= linea.quantity
            text = dom.createTextNode(str(int(cantidad_bultos)))
            CantidadBultos.appendChild(text)

            Subtotal= dom.createElement('Subtotal')
            remision.appendChild(Subtotal)
            text = dom.createTextNode(str(account_browse.amount_untaxed))
            Subtotal.appendChild(text)

            Descuentos= dom.createElement('Descuentos')
            remision.appendChild(Descuentos)
            text = dom.createTextNode('0')
            Descuentos.appendChild(text)

            ieps_amount = 0.0
            iva_amount = 0.0
            otros_impuestos = 0.0

            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
            ###### REVISAR EL NOMBRE DE LOS IMPUESTOS
            for impuesto in account_browse.tax_line:
                if 'IVA' in impuesto.name.upper():
                    iva_amount = impuesto.amount
                elif 'IEPS' in impuesto.name.upper():
                    ieps_amount = impuesto.amount
                else:
                    otros_impuestos+= impuesto.amount

            IEPS= dom.createElement('IEPS')
            remision.appendChild(IEPS)
            text = dom.createTextNode(str(ieps_amount))
            IEPS.appendChild(text)

            IVA= dom.createElement('IVA')
            remision.appendChild(IVA)
            text = dom.createTextNode(str(iva_amount))
            IVA.appendChild(text)

            OtrosImpuestos= dom.createElement('OtrosImpuestos')
            remision.appendChild(OtrosImpuestos)
            text = dom.createTextNode(str(otros_impuestos))
            OtrosImpuestos.appendChild(text)

            Total= dom.createElement('Total')
            remision.appendChild(Total)
            text = dom.createTextNode(str(account_browse.amount_total))
            Total.appendChild(text)

            CantidadPedidos= dom.createElement('CantidadPedidos')
            remision.appendChild(CantidadPedidos)
            text = dom.createTextNode(str(account_browse.cantidad_pedidos))
            CantidadPedidos.appendChild(text)

            FechaEntregaMercancia= dom.createElement('FechaEntregaMercancia')
            remision.appendChild(FechaEntregaMercancia)
            if account_browse.fecha_entrega_soriana:
                text = dom.createTextNode(str(account_browse.fecha_entrega_soriana)+"T00:00:00")
                FechaEntregaMercancia.appendChild(text)

            FolioNotaEntrada= dom.createElement('FolioNotaEntrada')
            remision.appendChild(FolioNotaEntrada)
            if account_browse.folio_entrada_soriana:
                text = dom.createTextNode(account_browse.folio_entrada_soriana)
                FolioNotaEntrada.appendChild(text)

            ##### Pedidos #####
            pedidos = dom.createElement('Pedidos')
            soriana.appendChild(pedidos)

            pedidos.setAttribute('Id',"1")
            pedidos.setAttribute('RowOrder',"1")

            Proveedor = dom.createElement('Proveedor')
            pedidos.appendChild(Proveedor)
            text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
            Proveedor.appendChild(text)

            Remision = dom.createElement('Remision')
            pedidos.appendChild(Remision)
            text = dom.createTextNode(serie_factura+'-'+account_browse.number)
            Remision.appendChild(text)

            FolioPedido = dom.createElement('FolioPedido')
            pedidos.appendChild(FolioPedido)
            text = dom.createTextNode(account_browse.no_pedido_soriana)
            FolioPedido.appendChild(text)

            Tienda = dom.createElement('Tienda')
            pedidos.appendChild(Tienda)
            text = dom.createTextNode(account_browse.tienda_entrega_soriana)
            Tienda.appendChild(text)

            CantidadArticulos = dom.createElement('CantidadArticulos')
            pedidos.appendChild(CantidadArticulos)
            cr.execute("select sum(quantity) from account_invoice_line where invoice_id=%s" % account_browse.id)
            cantidad_articulos = cr.fetchall()
            if  cantidad_articulos[0]:
                cantidad_articulos = cantidad_articulos[0][0]
            text = dom.createTextNode(str(int(cantidad_articulos)))
            CantidadArticulos.appendChild(text)

            ###### ARTICULOS ######
            i=1
            for line in account_browse.invoice_line:
                articulos = dom.createElement('Articulos')
                soriana.appendChild(articulos)

                articulos.setAttribute('Id',"Articulos1")
                articulos.setAttribute('RowOrder',str(i))

                Proveedor = dom.createElement('Proveedor')
                articulos.appendChild(Proveedor)
                text = dom.createTextNode(account_browse.partner_id.no_proveedor_addenda)
                Proveedor.appendChild(text)

                Remision = dom.createElement('Remision')
                articulos.appendChild(Remision)
                text = dom.createTextNode(serie_factura+'-'+account_browse.number)
                Remision.appendChild(text)

                FolioPedido = dom.createElement('FolioPedido')
                articulos.appendChild(FolioPedido)
                text = dom.createTextNode(account_browse.no_pedido_soriana)
                FolioPedido.appendChild(text)

                Tienda = dom.createElement('Tienda')
                articulos.appendChild(Tienda)
                text = dom.createTextNode(account_browse.tienda_entrega_soriana)
                Tienda.appendChild(text)

                Codigo = dom.createElement('Codigo')
                articulos.appendChild(Codigo)
                if line.codigo_soriana:
                    text = dom.createTextNode(line.codigo_soriana)
                    Codigo.appendChild(text)

                CantidadUnidadCompra = dom.createElement('CantidadUnidadCompra')
                articulos.appendChild(CantidadUnidadCompra)
                text = dom.createTextNode(str(int(line.quantity)))
                CantidadUnidadCompra.appendChild(text)

                CostoNetoUnidadCompra = dom.createElement('CostoNetoUnidadCompra')
                articulos.appendChild(CostoNetoUnidadCompra)
                text = dom.createTextNode(str(line.price_subtotal))
                CostoNetoUnidadCompra.appendChild(text)

                amount_ieps = 0.0
                amount_iva = 0.0
                subtotal_line = line.price_subtotal
                for tax in line.invoice_line_tax_id:
                    if 'IEPS' in tax.name.upper():
                        if tax.type == 'percent':
                            amount_ieps = tax.amount * 100
                        else:
                            amount_ieps = tax.amount
                    elif 'IVA' in tax.name.upper():
                        if tax.type == 'percent':
                            amount_iva = tax.amount * 100
                        else:
                            amount_ieps = tax.amount

                PorcentajeIEPS = dom.createElement('PorcentajeIEPS')
                articulos.appendChild(PorcentajeIEPS)
                text = dom.createTextNode(str("%.2f" % amount_ieps))
                PorcentajeIEPS.appendChild(text)

                PorcentajeIVA = dom.createElement('PorcentajeIVA')
                articulos.appendChild(PorcentajeIVA)
                text = dom.createTextNode(str("%.2f" % amount_iva))
                PorcentajeIVA.appendChild(text)

                i+=1
            data_xml = base64.encodestring(root.toxml('UTF-8'))
            xml_string = base64.decodestring(data_xml)
        return xml_string
account_invoice()

class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'
    _inherit = 'ir.attachment.facturae.mx'
    _columns = {
    }

    def add_addenta_xml(self, cr, ids, xml_res_str=None, comprobante=None, context=None):
        ### VERIFICAMOS QUE NO TENGA ADDENDA Y SI LA TIENE ENTONCES SIGA EL FLUJO NORMAL SI NO ENTONCES AGREGUE LA INFORMACION
        xml_data = base64.decodestring(base64.encodestring(xml_res_str.toxml('UTF-8')))
        have_addenda = 'cfdi:Addenda' in xml_data
        if have_addenda == True:
            return xml_res_str
        xml = super(ir_attachment_facturae_mx, self).add_addenta_xml(cr, ids, xml_res_str, comprobante, context=context)

        return xml
ir_attachment_facturae_mx()

class asistente_codigos_productos(osv.osv_memory):
    _name = 'asistente.codigos.productos'
    _description = 'Asistente Codigos Soriana'
    _columns = {
        'wizard_lines_ids': fields.one2many('asistente.codigos.productos.lineas', 'wizard_id', 'Lineas Factura'),
        'load_automatic': fields.boolean('Cargar Lineas'),
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
        account_invoice = self.pool.get('account.invoice')
        line_ids = []
        for rec in account_invoice.browse(cr, uid, [active_id], context=None):

            for line in rec.invoice_line:
                xline = (0,0,{
                    'invoice_line': line.id,
                    })
                line_ids.append(xline)
            res.update({'wizard_lines_ids':[x for x in line_ids]})
        return {'value':res}


    def assign_codigos(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            active_id = rec.active_id
            account_obj = self.pool.get('account.invoice')
            for line in rec.wizard_lines_ids:
                line.invoice_line.write({'codigo_soriana':line.codigo_soriana})
        return True

asistente_codigos_productos()

class asistente_codigos_productos_lineas(osv.osv_memory):
    _name = 'asistente.codigos.productos.lineas'
    _description = 'Asistente Lineas Manuales para Codigos Soriana'
    _columns = {
        'wizard_id': fields.many2one('asistente.codigos.productos','ID Ref'),
        'invoice_line': fields.many2one('account.invoice.line','Linea de Factura', readonly=True),
        'codigo_soriana': fields.char('Codigo Soriana', size=64, required=True),
    }
    _defaults = {
        }
asistente_codigos_productos_lineas()
