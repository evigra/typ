# coding: utf-8
{
    'name': 'Instance Creator',
    'summary': '''
    Instance creator for typ, this is the app.
    ''',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com',
    'license': 'AGPL-3',
    'category': 'Installer',
    'version': '8.0.0.1.1',
    'depends': [
        'account_aged_partner_balance_vw',
        'account_anglo_saxon',
        'account_asset',
        'account_budget',
        'account_check_writing',
        'account_closure_preparation',
        'account_followup',
        'account_financial_report',
        'account_ledger_report',
        'account_payment',
        'account_currency_tools',
        'claim_from_delivery',
        'contacts',
        'crm_helpdesk',
        'crm_profiling',
        'default_warehouse_from_sale_team',
        'hr_expense_replenishment_cancel',
        'hr_expense_replenishment_tax',
        'hr_payroll',
        'hr_timesheet_sheet',
        'ifrs_report',
        'invoice_number_view_tree',
        'l10n_mx_diot_report',
        'l10n_mx_facturae_pac_sf',
        'l10n_mx_sale_payment_method',
        'l10n_mx_facturae_pac_vauxoo',
        'l10n_mx_landing',
        'l10n_mx_accountinge',
        'marketing_campaign',
        'mrp_operations',
        'note',
        'partner_credit_limit',
        'product_available_by_warehouse',
        'product_extended_variants',
        'product_unique_serial',
        'purchase_double_validation',
        'purchase_requisition',
        'sale_margin',
        'sale_service',
        'stock_invoice_directly',
        'stock_landed_costs_segmentation',
        'warning',
        'stock_dropshipping',
        'product_customer_code',
        'typ_account',
        'typ_stock',
        'typ_partner',
        'typ_project_issue',
        'typ_sale',
        'typ_landed_costs',
        'typ_purchase',
        'typ_default_warehouse_from_sale_team',
        'typ_commision',
        'web_export_view',
        'typ_hr',
    ],
    'test': [
    ],
    'data': [
        'data/typ_paper_format.xml',
        'data/server_actions.xml',
        'data/set_configuration.yml',
        'data/ir_config_parameter.xml',
        'data/typ_security.xml',
        'report/invoice_report.xml',
        'report/report_invoice.xml',
    ],
    'demo': [
    ],
    "installable": True,
    "application": True,
    "post_init_hook": "_auto_install_stock_account_unfuck",
}
