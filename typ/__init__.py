# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import SUPERUSER_ID
# from . import report
# from . import models


def _auto_install_stock_account_unfuck(cr, registry):
    module_ids = registry['ir.module.module'].search(
            cr, SUPERUSER_ID, [
                ('name', '=', 'stock_account_unfuck'),
                ('state', '=', 'uninstalled')])
    registry['ir.module.module'].button_install(
            cr, SUPERUSER_ID, module_ids, {})
