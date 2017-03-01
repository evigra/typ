# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    coded by: Antonio Rogel <arogel@typrefrigeracion.com>
############################################################################
{
    'name': "Issue Tracking TYP",
    'license': "LGPL-3",
    'author': 'Vauxoo',
    'category': 'Project Management',
    'website': 'http://www.typrefrigeracion.com.mx/',
    'version': '8.0.0.1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'project_issue',
    ],
    # always loaded
    'data': [
        'views/project_issue_view.xml',
        'security/project_issue_security.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/project_issue_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
