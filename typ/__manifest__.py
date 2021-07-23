{
    "name": "Instance Creator",
    "summary": """
    Instance creator for typ, this is the app.
    """,
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com",
    "license": "LGPL-3",
    "category": "Installer",
    "version": "14.0.1.0.0",
    "depends": [
        # "l10n_mx_edi_hr_expense",
        # "l10n_mx_edi_customs_diot",
        # "l10n_mx_reports",
        # "l10n_mx_edi_partner_defaults",
        # "l10n_mx_import_taxes",
        "account_asset",
        "account_budget",
        "account_followup",
        "account_accountant",
        "account_payment",
        "l10n_mx_edi_extended",
        "fleet",
        "helpdesk",
        "mrp",
        "note",
        "stock_landed_costs",
        # 'typ_landed_costs', # --> TODO: Migrate
        # 'typ_account',  -> --> TODO: Partenr credit limit was rewrwitten. check if patches related to it
        # are necessary
        "typ_purchase",
        "typ_pos",
        # 'typ_stock_barcode',  --> TODO: Migrate
        "sale_margin",
        "delivery",
        "hr_payroll",
        # "crm",
        # 'payment_term_type',
        "base_automation",
        "typ_printing_report",
        # "typ_stock",
        # 'dev_invoice_multi_payment',  -> TODO: Check if it is really used in v14.0
        # 'login',
        'fleet',
        "website_sale",
        "website_blog",
        "website_crm",
        "auth_oauth",
        "barcodes_generator_product",
        "product_supplierinfo_for_customer_sale",
        "base_report_to_printer",
    ],
    "test": [],
    "data": [
        "data/settings.xml",
        # "data/data_facebook.xml",  -> TODO: review on v14.0
        "data/payment_terms.xml",
        "data/partner_tags.xml",
        "data/product_pricelist.xml",
        # "data/base_action_rule.xml",
        "data/email_template.xml",
        # "data/base_automation.xml",  -> # todo: move to code all the actions
        # "report/report_invoice.xml",   -> TODO: review on v14.0
        # "report/account_report_payment_receipt_templates.xml",   -> TODO: review on v14.0
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "security/ir_rules.xml",
        # "data/website_settings.yml",   -> TODO: review on v14.0
        # "data/account_fiscal_position.xml",   -> TODO: review on v14.0
        # "data/company.xml",   -> TODO: review on v14.0
        "data/categories.xml",  # -> TODO: review on v14.0
        # "data/website.xml",
        # "data/payment10.xml",  # TODO: This need to be refactored on 14.0 localization changed a lot
        "data/website_crm.xml",
        "data/hr_employee_check.xml",
        # Website stuff
        "views/paperformat.xml",
        "views/layout.xml",
        "views/product_market_type_views.xml",
        "views/product_category_views.xml",
        "views/account_views.xml",
        "views/account_move_views.xml",
        # "views/res_partner_warehouse_views.xml",
        "views/res_partner_views.xml",
        "views/res_config_views.xml",
        "views/product_views.xml",
        "views/purchase_order_views.xml",
        "views/sale_team_views.xml",
        "views/pricelist_views.xml",
        "views/sale_order_report.xml",
        "views/crm_lead_views.xml",
        "views/account_payment_views.xml",
        # "views/stock_views.xml",   -> TODO: review on v14.0
        "views/res_partner_views.xml",
        # "views/assets.xml",
        "views/templates.xml",
        # "views/helpdesk_views.xml",   -> TODO: review on v14.0
        "views/sale_order_views.xml",
        "views/hr_contract_views.xml",
        "views/hr_employee_beneficiary_views.xml",
        "views/hr_employee_auxiliar_view.xml",
        "views/hr_employee_reference_view.xml",
        "views/hr_employee_views.xml",
        "views/hr_employee_sed.xml",
        "views/fleet_views.xml",
        "views/hr_reports.xml",
        "views/hr_employee_report_pdf_view.xml",
        # "views/crm_lead.xml",   -> TODO: review on v14.0
        # #TODO: Note for website team, all this files must work standalone it does not make
        # sense have them sparated and explode everything if we change the theme.
        # "views/snippets.xml",  -> TODO: review on v14.0
    ],
    "demo": [
        # "demo/products.xml",
    ],
    "qweb": [
        # "static/src/xml/pos.xml",
    ],
    "installable": True,
    "application": True,
    # "post_init_hook": "_auto_install_stock_account_unfuck",
}
