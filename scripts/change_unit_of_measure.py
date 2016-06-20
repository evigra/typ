import click
import oerplib
# import psycopg2


@click.command()
@click.option('-ho', default='localhost',
              prompt='Odoo Host', help='Url for Odoo')
@click.option('-po', default='admin123', prompt='Password of Odoo',
              help='Password of user Odoo')
@click.option('-dbo', default='test_quant', prompt='Database Odoo',
              help='DB Name')
@click.option('-uo', default='admin', prompt='User Odoo', help='User of odoo')
@click.option('-pod', default=8072, prompt='Port Odoo', help='Port of Odoo')
@click.option('-du', default='josemorales', prompt='Database User',
              help='Name of database user')
@click.option('-dp', default='Karate.8', prompt='Database Password',
              help='Password of database user')
@click.option('-dpo', default=5432, prompt='Database Port',
              help='Port of Postgres')
@click.option('-dh', default='localhost', prompt='Database Host',
              help='Host of Postgres')
def check_attachments(ho, po, dbo, uo, pod, du, dp, dpo, dh):
    con = oerplib.OERP(ho, port=pod)
    con.login(user=uo, passwd=po, database=dbo)
    uom_ids = con.search('product.uom', [])
    for uom_id in uom_ids:
        uom_read = con.execute('product.uom', 'read',
                               uom_id, ['factor_inv'])
        if uom_read:
            old = uom_read.get('factor_inv')
            con.write('product.uom', [uom_id], {'factor_inv': 1})
            con.write('product.uom', [uom_id], {'factor_inv': round(old, 6)})

if __name__ == '__main__':
    check_attachments()
