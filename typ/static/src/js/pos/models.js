odoo.define("typ.pos_models", function (require) {
    "use strict";
    const models = require("point_of_sale.models");

    models.load_fields("res.partner", ["pricelist_ids"]);

    return models;
});
