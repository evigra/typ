# -*- coding: utf-8 -*-
{
    'name': "Typ Human Capital",
    'author': "Vauxoo, TyP refrigeracion",
    'website': "http://www.typrefrigeracion.com",
    'license': 'LGPL-3',
    'category': '',
    'version': '11.0.0.0.0',

    'depends': [
        'hr_payroll',
    ],

    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_inherit_view.xml',
        'views/hr_employee_auxiliar_view.xml',
        'views/hr_employee_beneficiary_view.xml',
        'views/hr_employee_reference_view.xml',
        'views/layouts.xml',
        'data/hr_employee_check.xml',
        'data/hr_security.xml',
        'reports/hr_employee_report_pdf_view.xml',
        'reports/hr_reports.xml',
        'views/hr_contract_inherit_view.xml',
    ],
    'installable': True,
}