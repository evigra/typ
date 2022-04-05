odoo.define("typ.address_remove_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "address_remove_tour",
        {
            test: true,
        },
        [
            {
                content: "Click on remove link from `John Doe` register",
                trigger: "a.delete_address_js:first",
            },
            {
                content: "Check if we were redirected to success page",
                trigger: "#wrap:has(h5:contains('SHIPPING INFORMATION'))",
            },
        ]
    );

    return {};
});
