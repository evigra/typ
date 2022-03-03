import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    init_stock_move_purchase_partner(cr)


def init_stock_move_purchase_partner(cr):
    """Initialize field "Vendor for purchase" in stock moves

    Even though that value is used only for new records, it's initialized for consistency
    and auditing purposes.
    """
    cr.execute(
        """
        -- Compute stock moves associated to an SO with purchase vendor
        WITH RECURSIVE move_purchase_partner AS (
            SELECT
                move.id,
                so_line.purchase_partner_id
            FROM
                stock_move AS move
            INNER JOIN
                sale_order_line AS so_line
                ON so_line.id = move.sale_line_id
            WHERE
                so_line.purchase_partner_id IS NOT NULL
        ),
        -- Retrieve all chained moves by recursively adding origin moves
        chained_move AS (
            SELECT
                id,
                purchase_partner_id
            FROM
                move_purchase_partner
            UNION
            SELECT
                move_orig_id AS id,
                purchase_partner_id
            FROM
                chained_move AS move
            INNER JOIN
                stock_move_move_rel AS move_rel
                ON move_rel.move_dest_id = move.id
        )
        UPDATE
            stock_move AS move
        SET
            purchase_partner_id = chained_move.purchase_partner_id
        FROM
            chained_move
        WHERE
            move.id = chained_move.id;
        """
    )
    _logger.info("Field 'Vendor for purchase' was initialized for %d stock moves", cr.rowcount)
