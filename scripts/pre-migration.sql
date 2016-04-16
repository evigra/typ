UPDATE stock_inventory_line SET product_uom=113 WHERE id=188465;
UPDATE stock_move SET product_uom=113 WHERE id=846516;
DROP FUNCTION IF EXISTS delete_old_views(view ir_ui_view);
CREATE OR REPLACE FUNCTION delete_old_views(view ir_ui_view)
RETURNS varchar AS $$
    DECLARE
        deleted varchar;
        inherit_view ir_ui_view%rowtype;
    BEGIN
        deleted := view.name;
        FOR inherit_view IN SELECT * FROM ir_ui_view WHERE inherit_id=view.id LOOP
            PERFORM delete_old_views(inherit_view);
        END LOOP;
        DELETE FROM ir_ui_view WHERE id=view.id;
        RETURN deleted; END;
    $$ LANGUAGE plpgsql;
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE arch ilike '%prodlot_id%' AND model='stock.move';
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE  model in ('stock.picking.in', 'stock.picking.out', 'stock.picking.int');
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE arch ilike '%stock_journal_id%' AND model='stock.picking';
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE arch ilike '%xpath%button%action_process%' AND model='stock.picking';
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE arch ilike '%procurement_id%' AND model='stock.warehouse.orderpoint';
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE arch ilike '%xpath%string%Expected Date%' AND model='purchase.order';
SELECT delete_old_views(views) AS name FROM ir_ui_view AS views WHERE arch ilike '%required_date_product%' AND model='purchase.order';
DELETE FROM ir_ui_view WHERE arch ilike '%xpath%button%429%';
