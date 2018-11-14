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
    'version': '11.0.0.0.2',
    'depends': [
        'l10n_mx_pos_cogs',
        'l10n_mx_edi_hr_expense',
        'l10n_mx_edi_customs',
        'l10n_mx_reports',
        'l10n_mx_edi_payment',
        'l10n_mx_edi_partner_defaults',
        'typ_landed_costs',
        'typ_account',
        'typ_purchase',
        'typ_pos',
        # 'account_aged_partner_balance_vw',
        'account_asset',
        'account_budget',
        'account_reports_followup',
        'account_accountant',
        'stock_by_warehouse_sale',
        # 'account_check_writing',
        # 'account_closure_preparation',
        # 'account_followup',
        # 'account_financial_report',
        # 'account_ledger_report',
        # 'account_payment',
        # 'account_currency_tools',
        # 'aging_due_report',
        # 'claim_from_delivery',
        # 'contacts',
        # 'crm_helpdesk',
        # 'crm_profiling',
        'fleet',
        # 'hr_expense_replenishment_cancel',
        # 'hr_expense_replenishment_tax',
        # 'hr_timesheet_sheet',
        # 'ifrs_report',
        # 'invoice_number_view_tree',
        # 'l10n_mx_diot_report',
        # 'l10n_mx_facturae_pac_sf',
        # 'l10n_mx_sale_payment_method',
        # 'l10n_mx_facturae_pac_vauxoo',
        # 'l10n_mx_accountinge',
        # 'marketing_campaign',
        # 'mrp_operations',
        'mrp',
        'note',
        # 'product_available_by_warehouse',
        # 'product_extended_variants',
        # 'product_supplierinfo_for_customer_sale',
        # 'product_unique_serial',
        # 'sale_service',
        # 'stock_invoice_directly',
        # 'warning',
        # 'stock_dropshipping',
        # 'typ_project_issue',
        # 'typ_commision',
        # 'web_export_view',
        'typ_hr',
        # 'typ_portal',
        # 'typ_printing_report',
    ],
    'test': [
    ],
    'data': [
        'data/typ_paper_format.xml',
        # 'data/set_configuration.yml',
        # 'data/typ_security.xml',
        'report/report_invoice.xml',
        'report/account_report_payment_receipt_templates.xml',
        # 'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    "installable": True,
    "application": True,
    # "post_init_hook": "_auto_install_stock_account_unfuck",
}
