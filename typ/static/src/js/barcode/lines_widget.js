odoo.define("typ.LinesWidget", function (require) {
    "use strict";

    const LinesWidget = require("stock_barcode.LinesWidget");

    LinesWidget.include({
        /**
         * @override this function to group the lines with the same product_id.
         *
         */
        init() {
            this._super.apply(this, arguments);
            if (this.model === "stock.picking" && this.mode === "receipt") {
                const lines = this.page.lines;
                const group_lines = {};
                lines.forEach((line) => {
                    // If the line comes from a product with lot tracking those lines must remain ungrouped to
                    // preserve the original Odoo behavior that allows to edit those kind of lines
                    const line_key =
                        line.product_id.tracking === "lot"
                            ? line.id + "-line-id"
                            : line.product_id.id;
                    // eslint-disable-next-line
                    if (!group_lines.hasOwnProperty(line_key)) {
                        group_lines[line_key] = {
                            display_name: line.display_name,
                            product_id: line.product_id,
                            line_products: [line],
                            line_ids: [line.id],
                            total_qty: line.product_uom_qty,
                            total_qty_done: line.qty_done,
                            product_uom_id: line.product_uom_id,
                            lot_id: line.lot_id,
                            lot_name: line.lot_name,
                            tag_ids: line.tag_ids,
                        };
                    } else if (line.product_uom_qty > 0 || line.qty_done > 0) {
                        group_lines[line_key].line_products.push(line);
                        group_lines[line_key].line_ids.push(line.id);
                        group_lines[line_key].total_qty += line.product_uom_qty;
                        group_lines[line_key].total_qty_done += line.qty_done;
                        group_lines[line_key].lot_id = line.lot_id;
                        if (line.lot_name) {
                            group_lines[line_key].lot_name += ", " + line.lot_name;
                        }
                    }
                });
                this.group_lines = group_lines;
            }
        },

        /**
         * @override this function to add the lines and mode of the picking without override the
         * _renderlines methods.
         */
        getProductLines: function (lines) {
            if (this.model !== "stock.picking" || this.mode !== "receipt") {
                return this._super.apply(this, arguments);
            }
            lines.__groupLines__ = this.group_lines;
            lines.__mode__ = this.mode;
            return this._super.apply(this, arguments);
        },

        /**
         * @override this function to increment the number of products scanned for the group line in the view.
         * _renderlines methods.
         */
        incrementProduct: function (
            id_or_virtual_id,
            qty,
            model,
            doNotClearLineHighlight
        ) {
            if (this.model !== "stock.picking" || this.mode !== "receipt") {
                return this._super.apply(this, arguments);
            }
            let $line = this.$(
                "div:not(.group_lines)[data-id='" + id_or_virtual_id + "']"
            );
            if (typeof id_or_virtual_id === "number") {
                const product_group_lines = this.$(
                    `div[data-group-product-id='${$line.data("product-id")}']`
                );
                for (const line of product_group_lines.toArray()) {
                    let line_ids = $(line).data("lines-ids");
                    try {
                        line_ids = line_ids.split(",").map(Number);
                    } catch (err) {
                        line_ids = [parseInt(line_ids, 10)];
                    }

                    if (line_ids.includes(id_or_virtual_id)) {
                        $line = $(line);
                        break;
                    }
                }
            }
            const qtyDone = parseFloat($line.find(".qty-done").text(), 10);
            $line
                .find(".qty-done")
                .text(parseFloat((qtyDone + qty).toPrecision(15)), 10);
            this._highlightLine($line, doNotClearLineHighlight);
        },

        /**
         * @override this function to add the lot name to the group line.
         */
        setLotName: function (id_or_virtual_id, lotName) {
            if (this.model !== "stock.picking" || this.mode !== "receipt") {
                return this._super.apply(this, arguments);
            }
            let $line = this.$(
                "div:not(.group_lines)[data-id='" + id_or_virtual_id + "']"
            );
            if (typeof id_or_virtual_id === "number") {
                const product_id = $line.data("product-id");
                $line = this.$("div[data-group-product-id='" + product_id + "']");
            }
            const $lotName = $line.find(".o_line_lot_name");
            let lotNameValue = $lotName.text();
            if (lotNameValue.includes("\n") && !lotNameValue.includes(",")) {
                lotNameValue = lotName;
            } else {
                lotNameValue += ", " + lotName;
            }
            const $span = $("<span>", {class: "o_line_lot_name", text: lotNameValue});
            $lotName.replaceWith($span);
        },

        /**
         * Overrides to handle the scroll into a scanned line when there is a small screen.
         *
         * @override
         * @private
         */
        _highlightLine: function ($line) {
            const data = this._super.apply(this, arguments);

            if (!$line.hasClass("o_line_completed")) {
                // If the screen is from a small device the screenOverflow is 'visible' and cannot scroll to the
                // same element (the scanned line) as when the screen is from a large device and its overflow is 'auto'
                const $screenContent = $(".o_barcode_client_action");
                const screenOverflow = $screenContent.css("overflow");
                const bodyToScroll =
                    screenOverflow === "auto"
                        ? this.$el.filter(".o_barcode_lines")
                        : $("body");
                bodyToScroll.animate(
                    {
                        scrollTop: $line.position().top,
                    },
                    500
                );
            }

            return data;
        },
    });
});
