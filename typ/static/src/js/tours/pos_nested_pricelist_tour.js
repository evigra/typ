odoo.define("typ.pos_nested_pricelist_tour", function (require) {
    "use strict";

    const {ProductScreen} = require("point_of_sale.tour.ProductScreenTourMethods");
    const {getSteps, startSteps} = require("point_of_sale.tour.utils");
    var tour = require("web_tour.tour");

    startSteps();

    // The table product as a price of 150 on the 1st pricelist item's based pricelist
    var product_name = "Table";
    ProductScreen.do.clickDisplayedProduct(product_name);
    ProductScreen.check.selectedOrderlineHas(product_name, "1.0", "150.0");

    // The drawer product as a price of 200 on the 2st pricelist item's based pricelist
    product_name = "Drawer Black";
    ProductScreen.do.clickDisplayedProduct(product_name);
    ProductScreen.check.selectedOrderlineHas(product_name, "1.0", "200.0");

    // The landing cost product is not on the pricelist, so it should take its sales price (75)
    product_name = "Landing Cost";
    ProductScreen.do.clickDisplayedProduct(product_name);
    ProductScreen.check.selectedOrderlineHas(product_name, "1.0", "75.0");

    tour.register("pos_nested_pricelist", {test: true}, getSteps());

    return {};
});
