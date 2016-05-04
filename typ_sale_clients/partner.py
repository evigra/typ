# -*- encoding: utf-8 -*-
from openerp.osv import osv,fields
from openerp import models
IMPORTANCIA = [
    ('AA','AA'),
    ('A','A'),
    ('B','B'),
    ('C','C'),
    ('NUEVO','NUEVO'),
    ('NEGOCIACION','NEGOCIACION'),
    ('EMPLEADO','EMPLEADO')
]

GIRO = [
    ('CONTRATISTAS','CON'),
    ('EMPRESAS','EMP'),
    ('MAYORISTAS','MAY'),
    ('NO_CLASIFICADO','NC'),
    ('EMPLEADO','EMPLEADO')
]

TIPO_CLIENTE = [
    ('CO','CO'),
    ('CN','CN'),
    ('CP','CP'),
    ('CR','CR'),
    ('ESP','ESP'),
    ('ALI','ALI'),
    ('SUP','SUP'),
    ('EMB','EMB'),
    ('OTR','OTR'),
    ('MC','MC'),
    ('MM','MM'),
    ('MF','MF'),
    ('NC','NC'),
    ('EMPLEADO','EMPLEADO')

]
TIPO_DEALER = [
    ('DP','DP'),
    ('DA','DA'),
    ('DE','DE')
]

REGION = [
    ('NOROESTE','NOROESTE'),
    ('OCCIDENTE','OCCIDENTE'),
    ('CENTRO','CENTRO'),
    ('NORESTE','NORESTE'),
    ('SURESTE','SURESTE'),
    ('SUR','SUR')
]

""" Creamos una clase para poner las constantes nombradas como campos de tipo seleccion """
class res_partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'importancia': fields.selection(IMPORTANCIA,'Importancia',help=""),
        'giro': fields.selection(GIRO,'Giro',help="NC - NO CLASIFICADO \n"
            "CON - CONTRATISTA\n"
            "EMP - EMPRESA \n"
            "MAY - MAYORISTA"),
        'tipo': fields.selection(TIPO_CLIENTE,'Tipo',help="CO - CONTRATISTA OPERADOR \n"
            "CN - CONTRATISTA OBRA NUEVA\n"
            "CP - CONTRATISTA PROFESIONAL\n"
            "CR - CONTRATISTA REFRIGERACION\n"
            "ESP - ESPECIFICADOR\n"
            "ALI - EMPRESA DE ALIMENTOS\n"
            "SUP - EMPRESA SUPERMERCADO\n"
            "EMB - EMBOTELLADORA\n"
            "OTR - OTRAS\n"
            "MC - MAYORISTA CONTRATISTA\n"
            "MM - MAYORISTA MAYORISTA\n"
            "MF - MAYORISTA FERRETERO\n"
            "NC - NO CLASIFICADO"),
        'dealer': fields.selection(TIPO_DEALER,'Tipo dealer',help="DP - DEALER PREMIER\n"
            "DA - DEALER AUTORIZADO\n"
            "DE - DEALER ESPORADICO"),
        'region': fields.selection(REGION,'Region'),
    }
