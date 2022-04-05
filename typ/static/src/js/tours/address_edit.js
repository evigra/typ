odoo.define("typ.address_edit_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "address_edit_tour",
        {
            test: true,
        },
        [
            {
                content: "Click on button `Edit Information` from `John Doe` register",
                trigger: "a.js_edit_address:first",
            },
            {
                content: "Edit phone number",
                trigger: "input[name=phone]",
                run: "text +52 55 2222 2222",
            },
            {
                content: "Edit neighborhood",
                trigger: "input[name=street2]",
                run: "text Another neighborhood",
            },
            {
                content: "Click on button `Save`",
                trigger: "button#save-record",
            },
            {
                content: "Check if we were redirected to success page",
                trigger: "#wrap:has(h5:contains('SHIPPING INFORMATION'))",
            },
        ]
    );

    return {};
});
