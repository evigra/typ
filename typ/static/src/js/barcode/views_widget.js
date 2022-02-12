odoo.define("typ.ViewsWidget", function (require) {
    "use strict";

    var ListView = require("web.ListView");
    var BarcodeViewsWidget = require("stock_barcode.ViewsWidget");

    BarcodeViewsWidget.include({
        /**
         * @override
         * This function was overridden to render a ListView when a user wants to edit
         * a grouped line (i.e a line with product with tracking by serial) rather a FormView or KanbanView
         * as in the original flow
         */
        _getViewController: function () {
            var self = this;
            if (self.view_type !== "list") {
                return this._super.apply(this, arguments);
            }

            const views = [[false, "list"]];

            var views_ref = {
                list: {list_view_ref: this.view},
            };
            var context = _.extend(
                {},
                this.defaultValue,
                this.context || {},
                views_ref[self.view_type]
            );
            return this.loadViews(this.model, context, views).then(function (
                fieldsViews
            ) {
                const domain = [
                    ["id", "in", self.params.ids || [self.params.currentId.toString()]],
                ];
                var params = _.extend(self.params || {}, {
                    context: context,
                    modelName: self.model,
                    userContext: self.getSession().user_context,
                    mode: self.mode,
                    withControlPanel: false,
                    withSearchPanel: false,
                    searchQuery: {
                        // This domain handles which records are going to be shown
                        domain: domain,
                        context: {
                            group_by_no_leaf: false,
                        },
                    },
                });
                const View = new ListView(fieldsViews.list, params);
                return View.getController(self);
            });
        },
    });
});
