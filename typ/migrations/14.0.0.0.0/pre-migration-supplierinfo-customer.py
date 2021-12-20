# This migration script was copied from:
# https://github.com/Vauxoo/product-attribute/blob/12.0/product_supplierinfo_for_customer/migrations/12.0.1.0.0/pre-migration.py
# The only modification is to don't migrate customerinfos if they were
# already migrated, to be able to run this script several times
from openupgradelib import openupgrade
from psycopg2 import sql


def _move_model_in_data(env, ids, old_model, new_model):
    renames = [
        ("mail_message", "model", "res_id"),
        ("mail_followers", "res_model", "res_id"),
        ("ir_attachment", "res_model", "res_id"),
        ("mail_activity", "res_model", "res_id"),
        ("ir_model_data", "model", "res_id"),
    ]
    for model, model_field, id_field in renames:
        openupgrade.logged_query(
            env.cr,
            sql.SQL(
                """UPDATE {model}
                SET {model_field} = %s
                WHERE {id_field} IN %s
                    AND {model_field} = %s"""
            ).format(
                model=sql.Identifier(model),
                model_field=sql.Identifier(model_field),
                id_field=sql.Identifier(id_field),
            ),
            (new_model, tuple(ids), old_model),
        )


def fill_product_customerinfo(env):
    cr = env.cr
    # Create customerinfos only if there are supplierinfos with type customer
    openupgrade.logged_query(
        cr,
        """
        SELECT id
        FROM product_supplierinfo
        WHERE supplierinfo_type = 'customer'""",
    )
    if not cr.rowcount:
        return
    openupgrade.logged_query(cr, "DROP TABLE IF EXISTS product_customerinfo")
    openupgrade.logged_query(
        cr,
        """
            CREATE TABLE product_customerinfo
            (LIKE product_supplierinfo INCLUDING ALL)""",
    )
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO product_customerinfo
        SELECT *
        FROM product_supplierinfo
        WHERE supplierinfo_type = 'customer'
        RETURNING id""",
    )
    ids = [x[0] for x in cr.fetchall()]
    if ids:
        _move_model_in_data(env, ids, "product.supplierinfo", "product.customerinfo")
        cr.execute("CREATE SEQUENCE IF NOT EXISTS product_customerinfo_id_seq")
        cr.execute("SELECT setval('product_customerinfo_id_seq', (SELECT MAX(id) FROM product_customerinfo))")
        cr.execute("ALTER TABLE product_customerinfo ALTER id SET DEFAULT NEXTVAL('product_customerinfo_id_seq')")
        openupgrade.logged_query(
            cr,
            """
            DELETE
            FROM product_supplierinfo
            WHERE supplierinfo_type = 'customer'""",
        )


def clean_action_domain(env):
    """
    For V11.0 product_supplierinfo_for_customer module add a
    domain ([('supplierinfo_type','=','supplier')]) in purchase action menu.
    In V12.0  supplierinfo_type has been removed, so we must clean the old
    stored action domain.
    """
    action = env.ref("product.product_supplierinfo_type_action")
    action.domain = False


@openupgrade.migrate()
def migrate(env, version):
    fill_product_customerinfo(env)
    clean_action_domain(env)
