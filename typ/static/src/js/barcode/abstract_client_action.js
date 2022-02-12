odoo.define("stock_barcode.ClientAction.typ", function (require) {
    "use strict";

    const ClientAction = require("stock_barcode.ClientAction");
    const {_t} = require("web.core");

    ClientAction.include({
        init() {
            this._super.apply(this, arguments);
            if (typeof this.context === "undefined") {
                this.context = {};
            }
        },
        _incrementLines: function (params) {
            const apply_original_method =
                this.actionParams.model !== "stock.picking" ||
                this.mode !== "receipt" ||
                this.context.lot_comes_from_step_product;
            if (apply_original_method) {
                return this._super.apply(this, arguments);
            }
            let line = this._findCandidateLineToIncrement(params);
            const lines = this.pages[this.currentPageIndex].lines;
            let isNewLine = false;
            const global_qty = 1;
            const line_total_qty = line.product_uom_qty - line.qty_done;
            if (line) {
                if (line.product_id.tracking === "serial") {
                    return this._super.apply(this, arguments);
                }
                this.processLine(line, lines, global_qty, line_total_qty, params);
            } else {
                isNewLine = true;
                line = this.processNewLine(line, params);
            }
            if (this.actionParams.model === "stock.picking") {
                if (params.lot_id) {
                    line.lot_id = [params.lot_id];
                }
                if (params.lot_name) {
                    line.lot_name = params.lot_name;
                }
            } else if (this.actionParams.model === "stock.inventory") {
                if (params.lot_id) {
                    line.prod_lot_id = [params.lot_id, params.lot_name];
                }
            }
            return {
                id: line.id,
                virtualId: line.virtual_id,
                lineDescription: line,
                isNewLine: isNewLine,
            };
        },

        processNewLine: function (line, params) {
            let newLine = line;
            params.qty_done = 1;
            if (
                params.product.tracking === "none" ||
                params.lot_id ||
                params.lot_name
            ) {
                params.product_qty = params.product_qty || 1;
                newLine = this._makeNewLine(params);
            } else {
                params.product_qty = 0;
                newLine = this._makeNewLine(params);
            }
            this._getLines(this.currentState).push(newLine);
            this.pages[this.currentPageIndex].lines.push(newLine);
            return newLine;
        },

        processLine: function (line, lines, global_qty, line_total_qty, params) {
            let global_quantity = global_qty;
            const scannedLine = line;
            if (
                scannedLine.qty_done !== scannedLine.product_uom_qty &&
                global_quantity > line_total_qty
            ) {
                global_quantity -= line_total_qty;
                scannedLine.qty_done += line_total_qty;
            } else {
                scannedLine.qty_done += params.product.qty || 1;
            }
            if (global_quantity > 0 && global_quantity < 1) {
                this.setLineQty(lines, scannedLine, global_quantity);
            }
        },

        setLineQty: function (lines, scannedLine, global_quantity) {
            let global_qty = global_quantity;
            for (const index in lines) {
                const order_line = lines[index];
                if (
                    scannedLine.id !== order_line.id &&
                    order_line.qty_done !== order_line.product_uom_qty &&
                    scannedLine.product_id.id === order_line.product_id.id
                ) {
                    const actual_line_qty =
                        order_line.product_uom_qty - order_line.qty_done;
                    if (global_qty >= actual_line_qty) {
                        global_qty -= actual_line_qty;
                        order_line.qty_done += actual_line_qty;
                        if (global_qty === 0) break;
                    } else {
                        order_line.qty_done += global_qty;
                        break;
                    }
                }
            }
        },

        /**
         * Handle what needs to be done when a product is scanned.
         * Inherit method that check if the prduct is required on the picking,
         * if not it will return an error. Otherwise, it will continue with
         * the normal process.
         * Also, we are setting the context `lot_comes_from_step_product` on
         * true when the product has as tracking strategy the lot, to avoid the
         * new mode of increment lines.
         *
         * @param {String} barcode scanned barcode
         * @param {Object} linesActions
         * @returns {Deferred}
         */
        _step_product: function (barcode) {
            const self = this;
            const _super = self._super.bind(self, ...arguments);
            return this._isProduct(barcode).then(
                function (product) {
                    if (product && !self.currentState.immediate_transfer) {
                        const lines = self._getLines(self.currentState);
                        let product_in_picking = false;
                        for (let line = 0; line < lines.length; line++) {
                            if (lines[line].product_id.id === product.id) {
                                product_in_picking = true;
                                break;
                            }
                        }
                        if (!product_in_picking) {
                            const errorMessage = _t(
                                "Ensure that you are scanning the same product."
                            );
                            return $.Deferred().reject(errorMessage);
                        }
                    }
                    self.context.lot_comes_from_step_product = false;
                    if (product && product.tracking === "lot") {
                        self.context.lot_comes_from_step_product = true;
                    }
                    return _super();
                },
                function () {
                    return _super();
                }
            );
        },

        /**
         * @override
         * This function was overridden to handle the edition of a grouped line with product tracking by
         * serial, if this is the case an array with the ids of the grouped lines is send to
         * _instantiateViewsWidget rather currentId, to check if a grouped line has a product with tracking by
         * serial use the is_serial attribute on the line (this is set in the xml template). The ids array and
         * is_serial variable comes from _onClickEditLine() function
         */
        _onEditLine: function (ev) {
            ev.stopPropagation();
            if (!ev.data.is_serial) {
                return this._super.apply(this, arguments);
            }
            this.linesWidgetState = this.linesWidget.getState();
            this.linesWidget.destroy();
            this.headerWidget.toggleDisplayContext("specialized");
            var self = this;
            this.mutex.exec(function () {
                return self._save().then(function () {
                    const ids = ev.data.ids;
                    const id = ev.data.id;
                    if (ids) {
                        self.ViewsWidget = self._instantiateViewsWidget({}, {ids: ids});
                    } else if (id) {
                        self.ViewsWidget = self._instantiateViewsWidget(
                            {},
                            {currentId: id, is_serial: true}
                        );
                    }
                    return self.ViewsWidget.appendTo(self.$(".o_content"));
                });
            });
        },
    });

    return ClientAction;
});
