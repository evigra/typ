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
from openerp import _
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp

class pedimento_custom(osv.osv):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'pedimento.custom'
    _description = 'Pedimentos Aduanales'
    _rec_name = 'complete_name'

    def _get_name(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=None):
            complete_name = rec.pedimento_sequence + ' / '+rec.port_entrance
            res[rec.id] = complete_name
        return res
    _columns = {
        'complete_name': fields.function(_get_name, string="Pedimento Aduanal", type="char", size=512, readonly=True, store=True),
        # 'name':fields.char('Aduana', size=128,required=True ),
        'date': fields.date('Fecha', required=True),
        'aduana_id': fields.many2one('res.partner','Agente Aduanal', required=True),
        'port_entrance': fields.char('Puerto de Entrada', size=128, required=True),
        'currency_id': fields.many2one('res.currency', 'Moneda', readonly=True),
        'type_change': fields.float('Tipo de Cambio', digits=(14,4), required=True),
        'notes': fields.text('Notas'),
        'pedimento_sequence': fields.char('Pedimento', size=128, required=True),
    }


    def _get_currency(self, cr, uid, context=None):
        currency = 0
        currency_obj = self.pool.get('res.currency')
        currency_ids = currency_obj.search(cr, uid, [('name','=','MXN')])
        if currency_ids:
            currency = currency_ids[0]
        return currency
        
    _defaults = {  
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d'),
        'currency_id': _get_currency,
        }
    _order = 'id desc'

    def create(self, cr, uid, vals, context=None):
        s = super(pedimento_custom, self).create(cr, uid, vals, context=context)
        config_obj = self.pool.get('pedimento.config')
        
        for obj in self.browse(cr, uid, [s], context=context):
            seq_id = 0
            config_id = config_obj.search(cr, uid, [('aduana_id','=',obj.aduana_id.id)])
            if not config_id:
                config_id = config_obj.search(cr, uid, [('general','=',True)])
            config_br = config_obj.browse(cr, uid, config_id, context=None)[0]
            seq_id = config_br.sequence_id.id
            if not obj.pedimento_sequence:
                seq_number = self.pool.get('ir.sequence').get_id(cr, uid, seq_id)
                self.message_post(cr, uid, [obj.id], body=_("Nuevo Pedimento para el Agente == %s ==") % (obj.name),  context=context)
                obj.write({'pedimento_sequence':seq_number})
        return s

pedimento_custom()


class pedimento_config(osv.osv):
    _name = 'pedimento.config'
    _description = 'Configuracion de Pedimentos'
    _rec_name = 'sequence_id' 
    _columns = {
        'sequence_id': fields.many2one('ir.sequence','Secuencia', required=True),
        'aduana_id': fields.many2one('res.partner','Aduana'),
        'general': fields.boolean('General', help='Define la Secuencia que utilizara para las Aduanas que no tengan una Secuencia en especifico'),
    }

    def _check_config(self, cr, uid, ids):
        config_obj = self.pool.get('pedimento.config')
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.general == False:
                return True
            else:
                config_id = config_obj.search(cr, uid, [('id','!=',rec.id),('general','=',True)])
                if config_id:
                    return False
        return True

    def _check_aduana(self, cr, uid, ids):
        config_obj = self.pool.get('pedimento.config')
        for rec in self.browse(cr, uid, ids, context=None):
            aduana_id = rec.aduana_id.id
            if not aduana_id:
                return True

            config_id = config_obj.search(cr, uid, [('id','!=',ids),('aduana_id','=',aduana_id)])
            if config_id:
                return False
        return True

    _constraints = [(_check_config, 'Error: Solo debe Existir un Registro de Configuración General', ['sequence_id']),
                    (_check_aduana, "Error: Solo debe Existir una Secuencia por Cada Aduana",['aduana_id']),] 
pedimento_config()


######### MODELOS PARA EL MANEJO DE LOS PEDIMENTOS COMO NUMEROS DE SERIE #############
class stock_production_lot_pedimento(osv.osv):

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'prefix', 'ref'], context)
        res = []
        for record in reads:
            name = record['name']
            prefix = record['prefix']
            if prefix:
                name = prefix + '/' + name
            if record['ref']:
                name = '%s [%s]' % (name, record['ref'])
            res.append((record['id'], name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        ids = []
        if name:
            ids = self.search(cr, uid, [('prefix', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    _name = 'stock.production.lot.pedimento'
    _description = 'Custom Number'

    _columns = {
        'name': fields.char('Pedimento', size=64, required=True, help="Numero de Pedimento Asignado para el producto: PREFIX/SERIAL [INT_REF]"),
        'ref': fields.char('Referencia Interna', size=256, help="Internal reference number in case it differs from the manufacturer's serial number"),
        'prefix': fields.char('Prefijo', size=64, help="Optional prefix to prepend when displaying this serial number: PREFIX/SERIAL [INT_REF]"),
        'product_id': fields.many2one('product.product', 'Producto', required=True, domain=[('type', '<>', 'service')]),
        'date': fields.datetime('Fecha de Creacion', required=True),
        'stock_available': fields.integer('Cantidad de Lotes Disponibles', readonly=True),
        'revisions': fields.one2many('stock.production.lot.revision.pedimento', 'lot_id', 'Revisiones'),
        'company_id': fields.many2one('res.company', 'Compania', select=True),
        'move_ids': fields.one2many('stock.move', 'pedimento_id', 'Movimientos para Este Pedimento', readonly=True),
        'pedimento_id': fields.many2one('pedimento.custom','Pedimento de Compra', readonly=True),
        #'move_ids': fields.one2many('stock.move', 'prodlot_id', 'Moves for this serial number', readonly=True),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'stock.production.lot.pedimento'),
        'product_id': lambda x, y, z, c: c.get('product_id', False),
    }
    _order = 'write_date desc' 
    _sql_constraints = [
        ('name_ref_uniq', 'unique (name, ref)', 'La Combinacion para el Nombre debe ser Unica !'),
    ]
    # def action_traceability(self, cr, uid, ids, context=None):
    #     """ It traces the information of a product
    #     @param self: The object pointer.
    #     @param cr: A database cursor
    #     @param uid: ID of the user currently logged in
    #     @param ids: List of IDs selected
    #     @param context: A standard dictionary
    #     @return: A dictionary of values
    #     """
    #     value=self.pool.get('action.traceability').action_traceability(cr,uid,ids,context)
    #     return value

    def copy(self, cr, uid, id, default=None, context=None):
        context = context or {}
        default = default and default.copy() or {}
        default.update(date=time.strftime('%Y-%m-%d %H:%M:%S'), move_ids=[])
        return super(stock_production_lot, self).copy(cr, uid, id, default=default, context=context)

stock_production_lot_pedimento()

class stock_production_lot_revision_pedimento(osv.osv):
    _name = 'stock.production.lot.revision.pedimento'
    _description = 'Custom Number Revision'

    _columns = {
        'name': fields.char('Revision', size=64, required=True),
        'description': fields.text('Descripvion'),
        'date': fields.date('Fecha Revision'),
        'indice': fields.char('Numero Revision', size=16),
        'author_id': fields.many2one('res.users', 'Author'),
        'lot_id': fields.many2one('stock.production.lot.pedimento', 'ID Referencia Pedimento', select=True, ondelete='cascade'),
        'company_id': fields.related('lot_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
    }

    _defaults = {
        'author_id': lambda x, y, z, c: z,
        'date': fields.date.context_today,
    }

stock_production_lot_revision_pedimento()


class stock_move(osv.osv):
    _name = 'stock.move'
    _inherit ='stock.move'
    _columns = {
    'pedimento_id': fields.many2one('stock.production.lot.pedimento','Pedimento', ondelete="cascade")
        }

    _default = {
        }

    def copy(self, cr, uid, id, default=None, context=None):
        # ref = self.pool.get('ir.sequence').get(cr, uid, 'pre.order.tpv')
        if not default:
            default = {}
        default.update({
                        
                        'pedimento_id': False,
                        })
        return super(stock_move, self).copy(cr, uid, id, default, context=context)
stock_move()