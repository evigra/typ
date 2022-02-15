odoo.define("typ.SetPricelistButton", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const SetPricelistButton = require("point_of_sale.SetPricelistButton");

    const SetPricelistButtonInherit = (SetPricelistButton) =>
        class extends SetPricelistButton {
            /**
             * When displaying dialog to select pricelist and a partner is selected, list only
             * the pricelists allowed for the selected partner (field pricelist_ids).
             */
            showPopup(name, props) {
                var partner = this.env.pos.get_client();
                if (partner && name == "SelectionPopup" && props && props.list) {
                    props.list = props.list.filter(
                        (pricelist) =>
                            pricelist.isSelected ||
                            partner.pricelist_ids.includes(pricelist.id)
                    );
                }
                return super.showPopup(name, props);
            }
        };

    Registries.Component.extend(SetPricelistButton, SetPricelistButtonInherit);

    return SetPricelistButtonInherit;
});
