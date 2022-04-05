odoo.define("typ.edit_information", function (require) {
    "use strict";

    require("web.dom_ready");

    var ajax = require("web.ajax");

    const $Edit_information = $(".account-form");

    if (!$Edit_information.length) {
        return $.Deferred().reject("DOM doesn't contain any '.account-form' element.");
    }

    function populate_states(env) {
        var self = $(env.target);
        if (self.val()) {
            ajax.jsonRpc("/shop/country_infos/" + $("#country_id").val(), "call", {
                mode: "shipping",
            }).then(function (data) {
                // Populate states and display
                var selectStates = self.closest("form").find("select[name='state_id']");
                // Don't reload state at first loading (done in qweb)
                if (data.states.length) {
                    selectStates.html("");
                    _.each(data.states, function (x) {
                        var opt = $("<option>")
                            .text(x[1])
                            .attr("value", x[0])
                            .attr("data-code", x[2]);
                        selectStates.append(opt);
                    });
                    selectStates.parent("div").show();
                } else {
                    selectStates.val("").parent("div").hide();
                }
            });
        }
    }

    if ($(".account-form").length) {
        $(".checkout_autoformat").on(
            "change",
            "select[name='country_id']",
            function (env) {
                populate_states(env);
            }
        );
    }
});
