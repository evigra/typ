# -*- coding: utf-8 -*-

__name__ = "Update invoice field date_paid"


def migrate(cr, version):
    query = ("""
        select distinct(ai.id) as invoice_id, aml2.date as date_paid
        from account_invoice as ai
        inner join account_move_line as aml on aml.move_id = ai.move_id and
            aml.account_id = ai.account_id
        inner join account_move_reconcile as amr on amr.id = aml.reconcile_id
        inner join account_move_line as aml2 on aml2.reconcile_id = amr.id
            and aml2.id <> aml.id
        where ai.state = 'paid' and ai.date_paid is Null and ai.type in
            ('out_invoice', 'out_refund')
        order by aml2.date desc
    """)
    cr.execute(query)
    result = cr.fetchall()
    for res in result:
        cr.execute(
            ('''UPDATE account_invoice set date_paid = %s where id = %s'''),
            (res[1], res[0]))
