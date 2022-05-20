odoo.define("typ.address_creation_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "address_creation_tour",
        {
            test: true,
        },
        [
            {
                content: "Click on button `Add an address`",
                trigger: "a#add_address",
            },
            {
                content: "Complete name",
                trigger: "input[name=name]",
                run: "text John Doe",
            },
            {
                content: "Complete phone number",
                trigger: "input[name=phone]",
                run: "text +52 55 1111 1111",
            },
            {
                content: "Complete Street",
                trigger: "input[name=street]",
                run: "text Morelos",
            },
            {
                content: "Complete Neighborhood",
                trigger: "input[name=street2]",
                run: "text Some neighborhood",
            },
            {
                content: "Complete Zip code",
                trigger: "input[name=zip]",
                run: "text 20020",
            },
            {
                content: "Complete Country",
                trigger: "select[name=country_id]",
                run: "text Mexico",
            },
            {
                content: "Complete State",
                trigger: "select[name=state_id]",
                timeout: 60000,
                run: "text Aguascalientes",
            },
            {
                content: "Complete City",
                trigger: "input[name=city]",
                run: "text Aguascalientes",
            },
            {
                content: "Click on button `Save`",
                trigger: "button#save-record",
            },
            {
                content: "Check if we were redirected to address list",
                trigger: ".o_portal li:contains('Address')",
            },
        ]
    );

    return {};
});
