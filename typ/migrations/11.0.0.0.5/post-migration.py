from odoo import SUPERUSER_ID, api


def clean_indext_content(cr, env):
    cr.execute("""UPDATE ir_attachment
                   SET index_content=Null
                  WHERE index_content IS NOT NULL""")


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        clean_indext_content(cr, env)
