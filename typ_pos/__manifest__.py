# -*- coding: utf-8 -*-
##############################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
##############################################################################
{
    "name":  "TYP POS",
    "summary":  "Display Stocks inside POS. Allow/Deny"
                " Order based on stocks.",
    "category":  "Point Of Sale",
    "version":  "11.0.1.0.0",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd., Vauxoo",
    "website":  "https://store.webkul.com/Odoo-POS-Stock.html",
    'license': 'Other proprietary',
    "live_test_url":  "http://odoodemo.webkul.com/?module="
                      "pos_stocks&version=10.0",
    "depends":  ['point_of_sale'],
    "data": [
        'data/res_groups.xml',
        'views/pos_stocks_view.xml',
        'views/template.xml',
        'views/pos_view.xml',
    ],
    "qweb":  ['static/src/xml/pos_stocks.xml'],
    "installable":  True,
    "auto_install":  False,
    "post_init_hook": "_set_new_group",
}
