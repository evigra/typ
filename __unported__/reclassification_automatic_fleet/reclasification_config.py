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

class reclasification_automatic_config(osv.osv):
    _name = 'reclasification.automatic.config'
    _description = 'Configuracion de Reclasificacion'
    _columns = {
    'name': fields.char('Descripcion', size=128),
    'company_id': fields.many2one('res.company','Compañia', required=True, ),
    # 'account_bridge': fields.many2one('account.account','Cuenta de Reclasificacion', help='Cuenta Transitoria para los Fletes',  required=True, ),
    # 'account_bridge_company': fields.many2one('account.account', 'Fletes Cuenta Transitoria de la Compañia', help='Cuenta Transitoria para la Compañia',  required=True, ),
    # 'account_bridge_consolidation': fields.many2one('account.account','Fletes Cuenta de Consolidacion', help='Aqui se Indican todas las Cuentas A Consolidar',  required=True, ),
    'account_bridge_lines': fields.one2many('reclasification.automatic.config.line','reclasification_id', 'Cuentas Transitoria Reclasificacion'),

    }

    def _check_config(self, cr, uid, ids):
        config_obj = self.pool.get('reclasification.automatic.config')
        for rec in self.browse(cr, uid, ids, context=None):
            config_id = config_obj.search(cr, uid, [('id','!=',rec.id)])
            if config_id:
                return False
        return True

    _constraints = [(_check_config, 'Error: Solo debe Existir un Registro de Configuración para la Reclasificacion', ['name']), ] 

    def _get_company(self, cr, uid, context=None):
        company = self.pool.get('res.company')
        company_id = company.search(cr, uid, [])
        sorted(company_id)
        company_id.sort()
        return company_id[0]

    _defaults = {  
        'name': 'Reclasificacion de Gasto de Fletes en cada Sucursal',
        'company_id': _get_company,
        }

reclasification_automatic_config()

class reclasification_automatic_config_line(osv.osv):
    _name = 'reclasification.automatic.config.line'
    _description = 'Linea de Configuracion'
    _rec_name = 'company_id' 
    _columns = {
    'reclasification_id': fields.many2one('reclasification.automatic.config','ID Referencia'),
    'company_id': fields.many2one('res.company', 'Compañia', required=True),
    #'account_bridge': fields.many2one('account.account','Cuenta de Reclasificacion', help='Define la Cuenta de Reclasificacion para la Compañia Hija, la cuenta debe pertener a la Compañia Padre de la Configuracion.', required=True),
    'account_bridge_shop': fields.many2one('account.account','Cuenta de Reclasificacion', help='Define la Cuenta de Reclasificacion para la Compañia Hija, la cuenta debe pertener a la Compañia Padre de la Configuracion.', required=True),
    }

    # def _check_config(self, cr, uid, ids):
    #     config_obj = self.pool.get('reclasification.automatic.config.line')
    #     for rec in self.browse(cr, uid, ids, context=None):
    #         config_id = config_obj.search(cr, uid, [('id','!=',rec.id),('company_id','=',rec.company_id.id)])
    #         if config_id:
    #             return False
    #     return True

    # _constraints = [(_check_config, 'Error: Solo debe Existir un Registro de Configuración por Sucursal', ['company_id']), ] 

reclasification_automatic_config_line()