import logging

from odoo import tools

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    rename_extids_typ_modules(cr)
    remove_deprecated(cr)
    remove_uncertified_data(cr)
    use_native_hr_marital_cohabitant(cr)
    sanitize_employee_blood_types(cr)
    rename_field_so_is_special(cr)
    deactivate_default_filters(cr)
    set_account_type_internal_group(cr)
    set_missing_company_stock_moves_lines(cr)
    set_missing_hr_expense_sheet_company(cr)
    remove_inconsistent_partner_bank(cr)
    create_missing_edi_payments(cr)
    set_pay_account_cash_journals(cr)
    set_missing_company_stock_locations(cr)


def rename_extids_typ_modules(cr):
    """Rename external IDs from __typ__** -> typ

    Since all typ_** modules will be combined with the main app (typ), all references
    was renamed to __typ__ in order to avoid data being deleted on app updating
    so now need to be renamed so records are not duplicated.
    """
    # Then, rename external IDs
    cr.execute(
        """
        UPDATE
            ir_model_data
        SET
            module = 'typ'
        WHERE
            module ilike '__typ__';
        """
    )


def use_native_hr_marital_cohabitant(cr):
    """Use the native  marital status "Legal Cohabitant"

    That marital status didn' exist in 11.0, so we added a custom one. But
    it's now supported, thanks to:
    https://github.com/odoo/odoo/commit/0eb58775c9e9
    """
    _logger.info("Updating employee's marital status to use the native cohabitant")
    cr.execute(
        """
        UPDATE
            hr_employee
        SET
            marital = 'cohabitant'
        WHERE
            marital = 'cohabiting';
        """
    )
    _logger.info("Updated %d employees", cr.rowcount)


def sanitize_employee_blood_types(cr):
    """Fix blood types to fid posible selections

    Blood type was a char and now it's a selection, and there are a few cases that need sanitizing.
    """
    _logger.info("Sanitizing employee's blood types")
    allowed_types = (
        "A-",
        "A+",
        "B-",
        "B+",
        "AB-",
        "AB+",
        "O-",
        "O+",
    )
    cr.execute(
        """
        UPDATE
            hr_employee
        SET
            blood_type = CASE
                WHEN
                    blood_type like '%%RH%%'
                THEN
                    REPLACE(REPLACE(blood_type, 'RH', ''), ' ', '')
                ELSE
                    NULL
                END
        WHERE
            blood_type NOT IN %s;
        """,
        [allowed_types],
    )
    _logger.info("Updated %d employees", cr.rowcount)


def rename_field_so_is_special(cr):
    """Rename sale order field "so" -> "is_special"

    The field name "so" doesn't give any useful information and it's not allowed by lints.
    """
    if tools.column_exists(cr, "sale_order", "so"):
        _logger.info("Renaming sale order field `so` -> `is_special`")
        tools.rename_column(cr, "sale_order", "so", "is_special")


def deactivate_default_filters(cr):
    """Deactivate user created filters, as some of them use old field names or unexisting models"""
    query = """
        UPDATE
            ir_filters
        SET
            is_default = false
        WHERE
            is_default = true
            AND create_uid > 2
    """
    cr.execute(query)


def set_account_type_internal_group(cr):
    """Set Missing internal_group on manual account type 'Cuentas de Orden'"""
    cr.execute("""UPDATE account_account_type SET internal_group='off_balance' WHERE internal_group IS NULL""")


def set_missing_company_stock_moves_lines(cr):
    """Some stock move lines missing company id"""
    query = """
        UPDATE
            stock_move_line
        SET
            company_id = (
                SELECT
                    id
                FROM
                    res_company
                LIMIT 1
            )
        WHERE
            company_id IS NULL
    """
    cr.execute(query)


def set_missing_hr_expense_sheet_company(cr):
    """Some hr.expense.sheet got to done and paid status without journal_id so setting the default journal"""
    cr.execute(
        """
        UPDATE
            hr_expense_sheet
        SET
            journal_id = (
                SELECT id FROM account_journal WHERE type = 'purchase' LIMIT 1
            )
        """
    )


MODELS_TO_DELETE = (
    "ir.actions.act_window",
    "ir.actions.act_window.view",
    "ir.actions.report.xml",
    "ir.actions.todo",
    "ir.actions.url",
    "ir.actions.wizard",
    "ir.cron",
    "ir.model",
    "ir.model.access",
    "ir.model.fields",
    "ir.module.repository",
    "ir.property",
    "ir.report.custom",
    "ir.report.custom.fields",
    "ir.rule",
    "ir.sequence",
    "ir.sequence.type",
    "ir.ui.menu",
    "ir.ui.view",
    "ir.ui.view_sc",
    "ir.values",
    "res.groups",
)


MODULES_TO_CLEAN = [
    "dev_invoice_multi_payment",
    "l10n_mx_edi_bank_statement",
    "l10n_mx_edi_cancellation_fields",
    "l10n_mx_edi_vendor_bills",
    "l10n_mx_edi_bank",
    "l10n_mx_pos_cogs",
    "login",
    "partner_credit_limit",
    "payment_conekta",
    "payment_term_type",
    "stock_cost_segmentation",
    "stock_landed_segmentation",
    "theme_typ",
    "typ_account",
    "typ_default_warehouse_from_sale_team",
    "typ_hr",
    "typ_landed_costs",
    "typ_pos",
    "typ_printing_report",
    "typ_purchase",
    "typ_sale",
    "typ_stock",
    "typ_stock_barcode",
]


def model_to_table(model):
    """
    Get a table name according to a model name In case the table name is set on
    an specific model manually instead the replacement, then you need to add it
    in the mapped dictionary.
    """
    model_table_map = {
        "ir.actions.client": "ir_act_client",
        "ir.actions.actions": "ir_actions",
        "ir.actions.report.custom": "ir_act_report_custom",
        "ir.actions.report.xml": "ir_act_report_xml",
        "ir.actions.act_window": "ir_act_window",
        "ir.actions.act_window.view": "ir_act_window_view",
        "ir.actions.url": "ir_act_url",
        "ir.actions.act_url": "ir_act_url",
        "ir.actions.server": "ir_act_server",
    }
    name = model_table_map.get(model)
    if name is not None:
        return name.replace(".", "_")
    if model is not None:
        return model.replace(".", "_")
    return ""


def remove_deprecated(cr):
    for module in MODULES_TO_CLEAN:
        cr.execute(
            """UPDATE ir_module_module
               SET (state, latest_version) = ('uninstalled', False)
               WHERE name = %s
            """,
            [module],
        )


def module_delete(cr, module_name):
    _logger.info("deleting module %s", module_name)

    def table_exists(table_name):
        query = """
            SELECT
                count(1)
            FROM
                information_schema.tables
            WHERE
                table_name = %s
                AND table_schema = 'public'
        """
        cr.execute(query, (table_name,))
        return cr.fetchone()[0]

    cr.execute(
        """
        SELECT res_id, model
        FROM ir_model_data
        WHERE module=%s
            AND model IN %s ORDER BY res_id desc""",
        (module_name, MODELS_TO_DELETE),
    )
    data_to_delete = cr.fetchall()
    for rec in data_to_delete:
        table = model_to_table(rec[1])
        cr.execute("SELECT count(*) FROM ir_model_data WHERE model = %s and res_id = %s", [rec[1], rec[0]])
        count1 = cr.dictfetchone()["count"]
        if count1 > 1:
            continue
        try:
            # ir_ui_view
            if table == "ir_ui_view":
                cr.execute("SELECT model " "FROM ir_ui_view WHERE id = %s", (rec[0],))
                t_name = cr.fetchone()
                table_name = model_to_table(t_name[0])
                cr.execute("SELECT viewname " "FROM pg_catalog.pg_views " "WHERE viewname = %s", [table_name])
                if cr.fetchall():
                    cr.execute("drop view " + table_name + " CASCADE")
                cr.execute("DELETE FROM ir_model_constraint " "WHERE model=%s", (rec[0],))
                cr.execute("DELETE FROM " + table + " WHERE inherit_id=%s", (rec[0],))
                view_exists = cr.fetchone()
                if bool(view_exists):
                    cr.execute("DELETE FROM " + table + " WHERE id=%s", (rec[0],))

            if table == "ir_model":
                if table_exists("ir_model_constraint"):
                    cr.execute("DELETE FROM ir_model_constraint " "WHERE model=%s", (rec[0],))
                if table_exists("ir_model_relation"):
                    cr.execute("DELETE FROM ir_model_relation " "WHERE model=%s", (rec[0],))
                cr.execute("DELETE FROM " + table + " WHERE id=%s", (rec[0],))
            else:
                cr.execute("DELETE FROM " + table + " WHERE id=%s", (rec[0],))

            # also DELETE dependencies:
            cr.execute("DELETE FROM ir_module_module_dependency " "WHERE module_id = %s", (rec[0],))
        except Exception as ex:
            msg = (
                (
                    """Module delete error\n
                   Model: %s, id: %s\n
                   Query: %s\n
                   Error: %s\n"
                   On Module: %s\n
                   """
                )
                % (rec[1], rec[0], cr.query, str(ex), module_name)
            )
            _logger.info(msg)
        else:
            _logger.info("Query on Else is %s", cr.query)

    cr.execute("DELETE FROM ir_model_data WHERE module=%s", (module_name,))
    cr.execute("UPDATE ir_module_module set state=%s WHERE name=%s", ("uninstalled", module_name))


def remove_uncertified_data(cr):
    for module in MODULES_TO_CLEAN:
        module_delete(cr, module)


def remove_inconsistent_partner_bank(cr):
    """There are some inconsistent partner banks, which are ones without partner"""
    cr.execute(
        """
        DELETE  FROM
            res_partner_bank
        WHERE
            partner_id IS NULL
        RETURNING acc_number;
        """
    )
    removed_accounts = [x[0] for x in cr.fetchall()]
    _logger.info("%s partner bank accounts were removed: %s", len(removed_accounts), removed_accounts)


def create_missing_edi_payments(cr):
    """Create EDI documents (account.edi.document) for payments

    Odoo doesn't create EDI documents when migrating payments, which makes CFDI-related fields
    (e.g. CFDI UUID) to don't be accessible.

    Issue reported to Odoo:
    https://www.odoo.com/my/task/2679440
    """
    _logger.info("Creating missing EDI documents for payments")
    cr.execute(
        """
        WITH payment_cfdi AS (
            SELECT
                MAX(id) AS id,
                res_id AS payment_id
            FROM
                ir_attachment
            WHERE
                res_model = 'account.payment'
                AND name ilike '%.xml'
            GROUP BY
                res_id
        ),
        payment_wo_edi AS (
            SELECT
                payment.id,
                payment.move_id
            FROM
                account_payment AS payment
            LEFT OUTER JOIN
                account_edi_document AS edi
                ON edi.move_id = payment.move_id
            WHERE
                edi.id IS NULL
        ),
        edi_format AS (
            SELECT
                id
            FROM
                account_edi_format
            WHERE
                code = 'cfdi_3_3'
            LIMIT 1
        )
        INSERT INTO account_edi_document (
            move_id,
            edi_format_id,
            attachment_id,
            state,
            create_uid,
            create_date,
            write_uid,
            write_date
        )
        SELECT
            payment.move_id,
            edi_format.id AS edi_format_id,
            cfdi.id AS attachment_id,
            CASE
                WHEN l10n_mx_edi_sat_status = 'cancelled' THEN 'cancelled'
                ELSE 'sent'
                END AS state,
            1 AS create_uid,
            NOW() at time zone 'UTC' AS create_date,
            1 AS write_uid,
            NOW() at time zone 'UTC' AS write_date
        FROM
            payment_wo_edi AS payment
        INNER JOIN
            account_move AS move
            ON move.id = payment.move_id
        INNER JOIN
            payment_cfdi AS cfdi
            ON cfdi.payment_id = payment.id
        CROSS JOIN
            edi_format
        WHERE
            move.state = 'posted';
        """
    )
    _logger.info("Created %d documents", cr.rowcount)


def set_pay_account_cash_journals(cr):
    """Set payment accounts for cash journals

    Set outstanding receipts and payment accounts with the default account so
    cash journals don't need to be reconciled when paying invoices and invoices
    are considered paid once payments are registered.
    """
    cr.execute(
        """
        UPDATE
            account_journal
        SET
            payment_debit_account_id = default_account_id,
            payment_credit_account_id = default_account_id
        WHERE
            type = 'cash'
            AND (
                payment_debit_account_id != default_account_id
                OR payment_credit_account_id != default_account_id
            );
        """
    )
    _logger.info("Payment accounts were set for %d journals", cr.rowcount)


def set_missing_company_stock_locations(cr):
    """Set missing company to non-external locations

    Company is missing in some locations that should have one, e.g. internal ones. That
    causes routes involving them to don't work correctly.

    In addition, quants are also updated, for consistency.
    """
    cr.execute(
        """
        WITH main_company AS (
            SELECT
                id
            FROM
                res_company
            LIMIT 1
        )
        UPDATE
            stock_location AS location
        SET
            company_id = main_company.id
        FROM
            main_company
        WHERE
            company_id IS NULL
            AND usage NOT IN ('view', 'customer', 'supplier')
        RETURNING location.id;
        """
    )
    location_ids = tuple(x[0] for x in cr.fetchall())
    _logger.info("Missing company was set for %d locations", len(location_ids))
    cr.execute(
        """
        WITH main_company AS (
            SELECT
                id
            FROM
                res_company
            LIMIT 1
        )
        UPDATE
            stock_quant
        SET
            company_id = main_company.id
        FROM
            main_company
        WHERE
            company_id IS NULL
            AND location_id IN %s
        """,
        [location_ids],
    )
    _logger.info(
        "Missing company was set for %d quants, corresponding to the %d locations just fixed",
        cr.rowcount,
        len(location_ids),
    )
