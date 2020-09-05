##############################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd.
#    (<https://webkul.com/>)
#
##############################################################################

from . import models
from . import report

def _set_new_group(cr, registry):
    cr.execute(
        '''
        UPDATE
            pos_config AS c
        SET
            group_pos_allow_payment_id = d.res_id
        FROM
            ir_model_data AS d
        WHERE
            d.module = 'typ_pos' AND
            d.name = 'allow_create_payment' AND
            d.model = 'res.groups'
        '''
    )
