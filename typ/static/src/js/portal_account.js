odoo.define("typ.portal_account", function (require) {
    "use strict";

    require("web.dom_ready");

    const Widget = require("web.Widget");

    const $Edit_information = $(".all_shipping");

    const ajax = require("web.ajax");

    if (!$Edit_information.length) {
        return $.Deferred().reject("DOM doesn't contain any '.all_shipping' element.");
    }

    const Edit_information = Widget.extend({
        events: {
            "click .js_edit_address": function (event) {
                event.preventDefault();
                $(event.currentTarget)
                    .parents("div.account-information")
                    .find("form.hide")
                    .attr("action", "/my/contact/edit")
                    .submit();
            },
            // Event to delete the selected address
            "click .delete_address_js": function (event) {
                event.preventDefault();
                console.log($(event.currentTarget).data("address-id"));
                ajax.jsonRpc("/delete-address", "call", {
                    address_id: $(event.currentTarget).data("address-id"),
                }).then(function () {
                    window.location.reload();
                });
            },
        },
    });

    $Edit_information.each(function () {
        const edit_information = new Edit_information();
        edit_information.attachTo($(this));
    });
});
