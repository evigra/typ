
__name__ = "Update invoice field date_paid"


def migrate(cr, version):
    query = ("""
        select ai.id as invoice_id, max(amr.create_date) as date_paid
        from account_invoice as ai
        inner join account_move_line as aml on aml.move_id = ai.move_id and
             aml.account_id = ai.account_id
        inner join account_move_reconcile as amr on amr.id = aml.reconcile_id
        where ai.state = 'paid' and ai.date_paid is not Null and
             ai.type in ('out_invoice', 'out_refund')
        group by ai.id
    """)
    cr.execute(query)
    result = cr.fetchall()
    for res in result:
        cr.execute(
            ('''UPDATE account_invoice set date_paid = %s where id = %s'''),
            (res[1], res[0]))
