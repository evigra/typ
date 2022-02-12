odoo.define("typ.picking_client_action", function (require) {
    "use strict";

    const PickingClientAction = require("stock_barcode.picking_client_action");
    const ViewsWidget = require("stock_barcode.ViewsWidget");

    PickingClientAction.include({
        /**
         * @override
         * This function was overridden to process the edition of a grouped line (i.e with product
         * with tracking by serial). If this is the case a list view, typ.stock_move_line_serial_list,
         * and view_type = list parameters are send to instantiate a ViewsWidget
         */
        _instantiateViewsWidget: function (defaultValues, params) {
            this._toggleKeyEvents(false);
            // If there is a currentId int he params this means that the line to edit
            // has not tracking by serial and the Odoo base flow is followed
            if (params.currentId && !params.is_serial) {
                return this._super.apply(this, arguments);
            }
            const view_type = "list";
            const mode = "edit";
            return new ViewsWidget(
                this,
                "stock.move.line",
                "typ.stock_move_line_serial_list",
                defaultValues,
                params,
                mode,
                view_type
            );
        },
    });
});
