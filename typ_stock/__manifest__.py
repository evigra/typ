############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Yennifer Santiago <yennifer@vauxoo.com>
#    planned by: Julio Serna <julio@vauxoo.com>
############################################################################
{
    'name': "Typ Stock",
    'version': '11.0.0.0.1',
    'license': 'LGPL-3',
    'category': '',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    # any module necessary for this one to work correctly
    'depends': [
        # 'default_warehouse_from_sale_team',
        # 'typ_purchase',
        # 'l10n_mx_landing',
        # 'product_unique_serial',
        # 'stock_analysis',
        # 'procurement_jit',
        # 'stock_move_entries',
        'sale_stock',
        'stock_no_negative',
        'stock_picking_show_return',
    ],
    # always loaded
    'data': [
        # 'views/email_template_view.xml',
        # 'data/ir_actions_server.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # 'data/base_action_rule.xml',
        # 'data/ir_cron.xml',
        'data/stock_sequence.xml',
        # 'views/procurement_rule_view.xml',
        'views/stock_view.xml',
        # 'views/stock_warehouse_view.xml',
        'views/stock_picking_view.xml',
        'views/product_view.xml',
        # 'views/stock_quant_view.xml',
        'views/stock_manual_transfer_view.xml',
        'views/view_procurement_compute_wizard_inh.xml',
        # 'wizard/stock_serial_view.xml',
        # 'wizard/pedimento_product_wizard.xml',
        # 'wizard/stock_transfer_details.xml',
        'report/report_stock_views.xml',
        'report/report_stockpicking.xml',
        'report/report_stockpicking_wobc.xml',
        'report/stock_report_deliveryslip.xml',
        # 'report/report_product_label.xml',
        # 'report/stock_analysis_view.xml',
        'views/stock_account_view.xml',
        'views/stock_inventory_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/stock_data.xml',
    ],
    'installable': True,
}
