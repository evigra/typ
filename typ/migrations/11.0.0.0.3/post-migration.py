from odoo import SUPERUSER_ID, api


def delete_payment_rule(cr, env):
    env['ir.rule'].browse(188).unlink()


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        delete_payment_rule(cr, env)
