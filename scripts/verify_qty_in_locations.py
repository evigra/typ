import click
import oerplib
# import psycopg2


@click.command()
@click.option('-ho', default='localhost',
              prompt='Odoo Host', help='Url for Odoo')
@click.option('-po', default='admin123', prompt='Password of Odoo',
              help='Password of user Odoo')
@click.option('-dbo', default='odoo70_jose_20160328', prompt='Database Odoo',
              help='DB Name')
@click.option('-uo', default='admin', prompt='User Odoo', help='User of odoo')
@click.option('-pod', default=12345, prompt='Port Odoo', help='Port of Odoo')
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
    print '1'
    con.login(user=uo, passwd=po, database=dbo)
    print '2'
    con2 = oerplib.OERP(ho, port=8072)
    con2.login(user=uo, passwd=po, database='test_quant')
    dest_loc = con.search('stock.location', [])
    products = con.search('product.product', [])
    print len(products)
    products = con.search('product.product', [('qty_available', '>', 0)])
    prods = []
    for prod in products:
        prod_source = con.execute('product.product', 'read', prod,
                                  ['qty_available','name'])
        if prod_source.get('qty_available') > 0:
            prods.append(prod_source.get('id'))
    print len(prods)
    for loca in dest_loc:
        for prod in prods:
            if con.execute('product.product', 'exists', prod) and \
                    con.execute('stock.location', 'exists', loca):
                context = {'location': loca,
                           'compute_child': False}
                prod_source = con.execute('product.product', 'read', prod,
                                          ['qty_available','name'], context)
                prod_dest = con2.execute('product.product', 'read', prod,
                                         ['qty_available', 'name'], context)
                if prod_source.get('qty_available') != \
                        prod_dest.get('qty_available'):
                    loc_name = con.read('stock.location', loca, ['usage']).get('usage')
                    click.echo('For the product {prod}, the '
                               'quantities is different '
                               'for location {loc}, {usa}, {qty} - {qtyy}'.
                               format(prod=prod, loc=loca,
                                      usa=loc_name,
                                      qty=prod_source.get('qty_available'),
                                      qtyy=prod_dest.get('qty_available')))
            else:
                click.echo('For the product {prod}, the '
                            'quantities is different '
                           'for location {loc} one of theses does not exists'.
                            format(prod=prod, loc=loca,
                                    ))


if __name__ == '__main__':
    check_attachments()
