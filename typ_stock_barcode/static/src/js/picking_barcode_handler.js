odoo.define('typ_stock_barcode.PickingBarcodeHandler', function (require) {
    "use strict";

    var FormController = require('web.FormController');


    FormController.include({
        _barcodeSelectedCandidate: function (candidate, record, barcode, activeBarcode) {
            var self = this;
            if (activeBarcode.widget === 'picking_barcode_handler' && candidate.data.lots_visible) {
                // the product is tracked by lot -> open the split lot wizard
                // save the record for the server to be aware of the operation
                return this.saveRecord(this.handle, {stayInEdit: true, reload: false}).then(function () {
                    return self._rpc({
                        model: 'stock.picking',
                        method: 'get_po_to_split_from_barcode',
                        args: [[record.data.id], barcode],
                    }).done(function (action) {
                        // the function returns an action (wizard)
                        self._barcodeStopListening();
                        self.do_action(action, {
                            on_close: function() {
                                self._barcodeStartListening();
                                self.update({}, {reload: true});
                            }
                        });
                    });
                });
            }
            if (activeBarcode.widget === 'picking_barcode_handler' && !candidate.data.lots_visible) {
                // the product is none tracking -> open the split lot wizard
                // save the record for the server to be aware of the operation
                return this.saveRecord(this.handle, {stayInEdit: true, reload: false}).then(function () {
                    return self._rpc({
                        model: 'stock.picking',
                        method: 'get_po_to_split_from_barcode_no_tracking',
                        args: [[record.data.id], barcode],
                    }).done(function (action) {
                        // the function returns an action (wizard)
                        self._barcodeStopListening();
                        self.do_action(action, {
                            on_close: function() {
                                self._barcodeStartListening();
                                self.update({}, {reload: true});
                            }
                        });
                    });
                });
            }
            return this._super.apply(this, arguments);
        },
        _barcodeWithoutCandidate: function (record, barcode, activeBarcode) {
            var self = this;
            if (activeBarcode.widget === 'picking_barcode_handler' && !record.data.lots_visible) {
                // the product is none tracking -> open the split lot wizard
                // save the record for the server to be aware of the operation
                return this.saveRecord(this.handle, {stayInEdit: true, reload: false}).then(function () {
                    return self._rpc({
                        model: 'stock.picking',
                        method: 'get_po_to_split_from_barcode_no_tracking',
                        args: [[record.data.id], barcode],
                    }).done(function (action) {
                        // the function returns an action (wizard)
                        self._barcodeStopListening();
                        self.do_action(action, {
                            on_close: function() {
                                self._barcodeStartListening();
                                self.update({}, {reload: true});
                            }
                        });
                    });
                });
            }
            return this._super.apply(this, arguments);
        },
    });
});
