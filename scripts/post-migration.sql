UPDATE stock_inventory_line SET product_uom=114 WHERE id=188465;
UPDATE stock_move SET product_uom=114 WHERE id=846516;
INSERT INTO product_price_history (create_uid, create_date, company_id, datetime, cost, product_template_id, write_date, write_uid)
(SELECT h.create_uid, h.create_date, h.company_id, h.write_date, h.standard_price, p.product_tmpl_id, h.write_date, h.write_uid FROM product_cost_multicompany AS h INNER JOIN product_product AS p ON p.id=h.product_id);
DROP FUNCTION IF EXISTS create_property_cost(product product_product);
CREATE OR REPLACE FUNCTION create_property_cost(product product_product)
RETURNS integer AS $$
    DECLARE
        property integer;
        history product_cost_multicompany%rowtype;
        mmodel integer;
        field integer;


    BEGIN
        mmodel := (SELECT id FROM ir_model WHERE model='product.template');
        field := (SELECT id FROM ir_model_fields WHERE model_id=mmodel AND name='standard_price');

        FOR history IN SELECT *  FROM product_cost_multicompany WHERE product_id=product.id ORDER BY write_date DESC LOOP
            IF NOT EXISTS (SELECT id FROM ir_property WHERE company_id=history.company_id AND name='standard_price' AND res_id='product.template,'|| product.product_tmpl_id) THEN
                INSERT INTO ir_property (create_uid, create_date, company_id,
                                         write_date, write_uid, value_float, res_id, fields_id,
                                         name, type) VALUES
                                        (history.create_uid,
                                         history.create_date,
                                         history.company_id,
                                         history.write_date,
                                         history.write_uid,
                                         history.standard_price,
                                         'product.template,'|| product.product_tmpl_id,
                                         field,
                                        'standard_price', 'float') RETURNING id INTO property;

            END IF;
        END LOOP;
        RETURN property; END;
    $$ LANGUAGE plpgsql;
SELECT create_property_cost(product) FROM product_product AS product;
