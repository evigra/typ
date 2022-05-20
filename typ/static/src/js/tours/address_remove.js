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
                content: "Check if we were redirected to address list",
                trigger: ".o_portal li:contains('Address')",
            },
        ]
    );

    return {};
});
