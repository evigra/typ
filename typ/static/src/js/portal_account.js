odoo.define("typ.portal_account", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.TyPortalAccount = publicWidget.Widget.extend({
        selector: ".all_shipping",
        events: {
            "click .js_edit_address": "_onClickAddress",
            "click .delete_address_js": "_onDeleteAddress",
        },
        _onClickAddress(event) {
            event.preventDefault();
            var address_id = $(event.currentTarget).data("address-id");
            var $form = this.$el.find(".js_form_edit");
            $form.find("[name='partner_id']").val(address_id);

            $form.submit();
        },
        _onDeleteAddress(event) {
            event.preventDefault();
            var params = {address_id: $(event.currentTarget).data("address-id")};
            this._rpc({
                route: "/delete-address",
                params,
            }).then(function () {
                window.location.reload();
            });
        },
    });
});
