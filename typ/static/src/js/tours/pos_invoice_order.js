odoo.define("typ.pos_invoice_order_tour", function (require) {
    "use strict";

    const {makeFullOrder} = require("point_of_sale.tour.CompositeTourMethods");
    const {getSteps, startSteps} = require("point_of_sale.tour.utils");
    var tour = require("web_tour.tour");

    startSteps();

    makeFullOrder({
        orderlist: [["Table", "2", "150"]],
        customer: "Azure Interior",
        // Payment amount: 300 (2*150) + 16% taxes
        payment: ["Cash", "348"],
    });

    tour.register("pos_invoice_order", {test: true}, getSteps());

    return {};
});
