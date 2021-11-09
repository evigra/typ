odoo.define("typ.lead_from_product_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "lead_from_product_tour",
        {
            test: true,
        },
        [
            {
                content: "Select product `Drawer Black`",
                trigger: "a:contains(Drawer Black)",
            },
            {
                content: "Click on button `Request a quotation`",
                trigger: "a#request_quotation",
            },
            {
                content: "Check the product name is displayed and readonly",
                trigger:
                    "input[id=opportunity0_product_name][value='[FURN_8900] Drawer Black'][readonly]",
            },
            {
                content: "Complete name",
                trigger: "input[name=contact_name]",
                run: "text John Doe",
            },
            {
                content: "Complete phone number",
                trigger: "input[name=phone]",
                run: "text +52 55 1111 1111",
            },
            {
                content: "Complete Email",
                trigger: "input[name=email_from]",
                run: "text john@typ.mx",
            },
            {
                content: "Complete Subject",
                trigger: "input[name=name]",
                run: "text Test subject",
            },
            {
                content: "Complete Description",
                trigger: "textarea[name=description]",
                run: "text Some description",
            },
            {
                content: "Send the form",
                trigger: ".s_website_form_send",
            },
            {
                content: "Check we were redirected to the success page",
                trigger: "#wrap:has(h1:contains('Thank You!'))",
            },
        ]
    );

    return {};
});
