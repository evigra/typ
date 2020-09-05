
import collections
from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


IMPORTANCE = [
    ('AA', 'AA'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('X', 'X'),
    ('NEW', 'NEW'),
    ('NEGOTIATION', 'NEGOTIATION'),
    ('EMPLOYEE', 'EMPLOYEE'),
    ('NOT CLASSIFIED', 'NOT CLASSIFIED')
]

POTENTIAL = [
    ('AA', 'AA'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('X', 'X'),
    ('NEW', 'NEW'),
    ('NEGOTIATION', 'NEGOTIATION'),
    ('EMPLOYEE', 'EMPLOYEE'),
    ('NOT CLASSIFIED', 'NOT CLASSIFIED')
]

BUSINESS_ACTIVITY = [
    ('CONTRACTORS', 'CON'),
    ('COMPANY', 'COM'),
    ('WHOLESALERS', 'WHO'),
    ('NOT CLASSIFIED', 'NOT CLASSIFIED'),
    ('EMPLOYEE', 'EMPLOYEE'),
    ('PUBLIC', 'PUBLIC')
]

CLIENT_TYPE = [
    ('OC', 'OC'),
    ('NC', 'NC'),
    ('PC', 'PC'),
    ('RC', 'RC'),
    ('ESP', 'ESP'),
    ('FSC', 'FSC'),
    ('SUP', 'SUP'),
    ('BOT', 'BOT'),
    ('OTH', 'OTH'),
    ('WHC', 'WHC'),
    ('WW', 'WW'),
    ('WI', 'WI'),
    ('NOT CLASSIFIED', 'NOT CLASSIFIED'),
    ('EMPLOYEE', 'EMPLOYEE'),
    ('PUBLIC', 'PUBLIC')
]
DEALER_TYPE = [
    ('PD', 'PD'),
    ('AD', 'AD'),
    ('SD', 'SD')
]

REGION = [
    ('NORTHWEST', 'NORTHWEST'),
    ('WEST', 'WEST'),
    ('CENTER', 'CENTER'),
    ('NORTHEAST', 'NORTHEAST'),
    ('SOUTHEAST', 'SOUTHEAST'),
    ('SOUTH', 'SOUTH')
]


class ResPartner(models.Model):

    _inherit = 'res.partner'
    importance = fields.Selection(IMPORTANCE)
    potential_importance = fields.Selection(POTENTIAL)
    business_activity = fields.Selection(BUSINESS_ACTIVITY,
                                         help="Not classified \n"
                                         "CON - Contractor\n"
                                         "COM - Company\n"
                                         "WHO - Wholesaler")
    partner_type = fields.Selection(CLIENT_TYPE,
                                    help="OC - Operator contractor\n"
                                    "NC - New work contractor\n"
                                    "PC - Professional contractor\n"
                                    "RC - Refrigeration contractor\n"
                                    "SP - Specifier\n"
                                    "FSC - Foodstuff company\n"
                                    "SUP - Supermarket company\n"
                                    "BOT - Bottler\n"
                                    "OTH - Others\n"
                                    "WHC - Wholesaler contractor\n"
                                    "WW - Wholesaler wholesaler\n"
                                    "WI - Wholesaler ironmonger")
    dealer = fields.Selection(DEALER_TYPE, 'Dealer type',
                              help="PD - Premier dealer\n"
                              "AD - Authorized dealer\n"
                              "SD - Sporadic dealer")
    region = fields.Selection(REGION)
    res_warehouse_ids = fields.One2many(
        comodel_name='res.partner.warehouse', inverse_name='partner_id',
        string='Warehouse configuration', help='Configurate salesman and'
        ' credit limit to each warehouse')

    @api.multi
    @api.constrains('res_warehouse_ids')
    def unique_conf_partner_warehouse(self):
        for res in self:
            warehouse_ids = [res_wh.warehouse_id for res_wh in
                             res.res_warehouse_ids]
            dict_values = dict(collections.Counter(warehouse_ids))
            for key in dict_values.keys():
                if dict_values[key] > 1:
                    raise ValidationError(
                        _('There is more than one configuration for warehouse'
                          ' %s. It must have only one configuration for each'
                          ' warehouse') % (key.name))
