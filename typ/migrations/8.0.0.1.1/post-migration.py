
__name__ = "Stock Account Unfuck - Installation"


def migrate(cr, version):
    cr.execute("""
        UPDATE ir_module_module
        SET state='to install'
        WHERE name = 'stock_account_unfuck';
    """)
