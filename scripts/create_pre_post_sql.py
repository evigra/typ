import click
import os
import subprocess
import oerplib
# import psycopg2


@click.command()
@click.option('-ho', default='erp70.test.typrefrigeracion.com',
              prompt='Odoo Host', help='Url for Odoo')
@click.option('-po', default='admin123', prompt='Password of Odoo',
              help='Password of user Odoo')
@click.option('-dbo', default='odoo70_v2_20160328', prompt='Database Odoo',
              help='DB Name')
@click.option('-uo', default='admin', prompt='User Odoo', help='User of odoo')
@click.option('-pod', default=7080, prompt='Port Odoo', help='Port of Odoo')
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
    # conp = psycopg2.connect("dbname='{dn}' user='{du}' host='{dh}' "
    #                         "password='{dp}' port={dpo}".format(dn=dbo,
    #                                                             du=du,
    #                                                             dh=dh,
    #                                                             dp=dp,
    #                                                             dpo=dpo))
    # cr = conp.cursor()
    # cr.execute("""SELECT am.id FROM account_move AS am
    #               INNER JOIN account_journal aj ON am.journal_id = aj.id
    #               WHERE aj.type != 'situation' AND
    #                     am.company_id=1""")
    # am_ids = cr.fetchall()
    modules_ids = con.search('ir.module.module',
                             [('state', '=', 'installed')])
    lins = []
    for mod_id in modules_ids:
        mod_read = con.execute('ir.module.module', 'read',
                               mod_id, ['name'])
        if mod_read:
            name = mod_read.get('name')
            lins.append(name)

            # for fpath in os.popen("find ../ -name %s -type d" % name):
            #     subprocess.Popen(('cp', '-r', fpath.replace('\n', ''), '.'))
            #     # os.popen2('cp -r %s /home/odoo/instance/extra_addons/modules_installed/' % fpath)
            #     break
    print lins
    print len(lins)

if __name__ == '__main__':
    check_attachments()
