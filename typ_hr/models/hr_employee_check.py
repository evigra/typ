# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from odoo import models, fields

DOC = [
    ('RD', 'Recruitment documents'),
    ('CD', 'Company documents')
]


class HrEmployeeCheck(models.Model):
    _name = 'hr.employee.check'
    name = fields.Char()
    doc_type = fields.Selection(DOC)
