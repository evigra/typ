# coding: utf-8
from odoo import SUPERUSER_ID, api


def delete_view(cr):
    # Delete view with incorrect id the module typ
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        view = env.ref(
            'product.product_search_form_inherit_typ',
            raise_if_not_found=False)
        view.unlink()


def migrate(cr, version):
    return