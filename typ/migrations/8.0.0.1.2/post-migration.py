# -*- coding: utf-8 -*-
from openerp import api, SUPERUSER_ID

__name__ = "Cleaning Warnings"


def remove_warning(cr):
    """Removing Warnings generated when the database was migrated
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        ids = []
        for i in env['ir.model'].search([]):
            try:
                env[i.model]
            except:
                ids.append(i.id)
        if ids:
            env.cr.execute(
                '''DELETE FROM
                       ir_model_relation
                   WHERE
                       model IN %s ''', (tuple(ids), ))
            env.cr.execute(
                '''DELETE FROM
                       ir_model_constraint
                   WHERE
                       model IN %s''', (tuple(ids), ))
            env.cr.execute(
                '''UPDATE
                       hr_job
                   SET
                       alias_id=null
                   WHERE
                       alias_id IN (SELECT
                                       id
                                    FROM
                                       mail_alias
                                    WHERE
                                        alias_model_id IN %s )'''
                % (tuple(ids),))
            env.cr.execute(
                '''DELETE FROM
                       ir_model
                   WHERE
                       id in %s''', (tuple(ids),))
            env.cr.execute(
                '''DELETE FROM
                       ir_model
                   WHERE
                       id in %s''', (tuple(ids),))
            env.cr.execute(
                """UPDATE
                       ir_module_module
                   SET
                       state='uninstalled'
                   WHERE
                       name='portal_event'""")
            env.cr.execute(
                """DELETE FROM
                       mail_followers as f1
                   USING
                       mail_followers AS f2
                   WHERE f1.res_model = f2.res_model AND
                         f1.res_id=f2.res_id AND
                         f1.partner_id=f2.partner_id AND
                         f1.id>f2.id;""")


def migrate(cr, version):
    if not version:
        return
    remove_warning(cr)
