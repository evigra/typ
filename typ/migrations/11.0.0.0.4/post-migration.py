from odoo import SUPERUSER_ID, api


def inactive_company_rules(cr, env):
    env['ir.rule'].search([
        ('domain_force', 'ilike', 'company')]).write({'active': False})


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        inactive_company_rules(cr, env)
