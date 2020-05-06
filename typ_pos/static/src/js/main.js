odoo.define('typ_pos.pos_stock',function(require) {
    "use strict";
    var models = require('point_of_sale.models');
    var PosBaseWidget = require('point_of_sale.BaseWidget');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var rpc = require('web.rpc');
    var SuperNumpadState = models.NumpadState.prototype;
    var model_list = models.PosModel.prototype.models
    var _t = core._t;
    var _super_posmodel = models.PosModel.prototype;
    var exports = models.exports
    var round_pr = utils.round_precision;

    models.load_fields('product.product', ['qty_available', 'virtual_available', 'outgoing_qty', 'type']);
    models.load_fields('res.partner', ['pricelist_ids']);
    var product_model = null;
    var user_model = null;
    for(var i = 0,len = model_list.length;i<len;i++){
        if(model_list[i].model == "product.product"){
            product_model = model_list[i];
        } else if(model_list[i].model == "res.users"){
            user_model = model_list[i];
        } else if(product_model && user_model){
            break;
        }
    }

    user_model.loaded = function(self,users){
            // we attribute a role to the user, 'cashier' or 'manager', depending
            // on the group the user belongs.
            var pos_users = [];
            var current_cashier = self.get_cashier();
            for (var i = 0; i < users.length; i++) {
                var user = users[i];
                user.skip_payment = false;
                for (var j = 0; j < user.groups_id.length; j++) {
                    var group_id = user.groups_id[j];
                    if (group_id === self.config.group_pos_manager_id[0]) {
                        user.role = 'manager';
                        break;
                    } else if (group_id === self.config.group_pos_user_id[0]) {
                        user.role = 'cashier';
                    } else if (group_id === self.config.group_pos_allow_payment_id[0]) {
                        user.skip_payment = true;
                    }
                }
                if (user.role) {
                    pos_users.push(user);
                }
                // replace the current user with its updated version
                if (user.id === self.user.id) {
                    self.user = user;
                }
                if (user.id === current_cashier.id) {
                    self.set_cashier(user);
                }
            }
            self.users = pos_users;
        },

    product_model.context= function(self){ return {location: self.config.stock_location_id[0]}; },
    product_model.loaded = function(self,products){
        var using_company_currency = self.config.currency_id[0] === self.company.currency_id[0];
        var conversion_rate = self.currency.rate / self.company_currency.rate;
        if(self.config.wk_hide_out_of_stock){
            var available_product = [];
            for(var i = 0,len = products.length; i<len; i++){
                switch(self.config.wk_stock_type){
                    case'forecasted_qty':
                        if(products[i].virtual_available>0||products[i].type == 'service')
                            available_product.push(products[i]);
                        break;
                    case'virtual_qty':
                        if((products[i].qty_available-products[i].outgoing_qty)>0||products[i].type == 'service')
                            available_product.push(products[i]);
                        break;
                    default:
                        if(products[i].qty_available>0||products[i].type == 'service')
                            available_product.push(products[i]);
                }
            }
            products = available_product;
        }
        var results={};
        for(var i = 0,len=products.length;i<len;i++){
            switch(self.config.wk_stock_type){
                case'available_qty':
                    results[products[i].id]=products[i].qty_available;
                    break;
                case'forecasted_qty':
                    results[products[i].id]=products[i].virtual_available;
                    break;
                default:
                    results[products[i].id]=products[i].qty_available-products[i].outgoing_qty;
            }
        }
        self.set({
            'wk_product_qtys' : results
        });
        self.chrome.wk_change_qty_css();
        self.db.add_products(_.map(products, function (product) {
            if (!using_company_currency) {
                product.lst_price = round_pr(product.lst_price * conversion_rate, self.currency.rounding);
            }
            product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
            return new models.Product({}, product);
        }));
    },

    models.PosModel = models.PosModel.extend({
        push_and_invoice_order: function(order) {
            var self = this;
            if (order != undefined) {
                var wk_order_line = order.get_orderlines();

                for (var j = 0; j < wk_order_line.length; j++) {
                    self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                }
            }
            var push = _super_posmodel.push_and_invoice_order.call(this, order);

            return push;
        },

        push_order: function(order) {
            var self = this;
            if (order != undefined) {
                var wk_order_line = order.get_orderlines();

                for (var j = 0; j < wk_order_line.length; j++) {
                    self.get('wk_product_qtys')[wk_order_line[j].product.id] = self.get('wk_product_qtys')[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                }
            }
            var push = _super_posmodel.push_order.call(this, order);
            return push;
        },

    });

    PosBaseWidget.include({
        get_information: function(wk_product_id) {
            self = this;
            if (self.pos.get('wk_product_qtys'))
                return self.pos.get('wk_product_qtys')[wk_product_id];
        },
        wk_change_qty_css: function() {
            self = this;
            var wk_order = self.pos.get('orders');
            var wk_p_qty = new Array();
            var wk_product_obj = self.pos.get('wk_product_qtys');
            if (wk_order) {
                for (var i in wk_product_obj) {
                    wk_p_qty[i] = self.pos.get('wk_product_qtys')[i];
                }
                for (var i = 0; i < wk_order.length; i++) {
                    var wk_order_line = wk_order.models[i].get_orderlines();
                    for (var j = 0; j < wk_order_line.length; j++) {
                        wk_p_qty[wk_order_line[j].product.id] = wk_p_qty[wk_order_line[j].product.id] - wk_order_line[j].quantity;
                        var qty = wk_p_qty[wk_order_line[j].product.id];
                        if (qty)
                            $("#qty-tag" + wk_order_line[j].product.id).html(qty);
                        else
                            $("#qty-tag" + wk_order_line[j].product.id).html('0');
                    }
                }
            }
        }
    });

    models.Product = models.Product.extend({
        get_price: function(pricelist, quantity){
            var self = this;
            var date = moment().startOf('day');

            // In case of nested pricelists, it is necessary that all pricelists are made available in
            // the POS. Display a basic alert to the user in this case.
            if (pricelist === undefined) {
                alert(_t(
                    'An error occurred when loading product prices. ' +
                    'Make sure all pricelists are available in the POS.'
                ));
            }

            var category_ids = [];
            var category = this.categ;
            while (category) {
                category_ids.push(category.id);
                category = category.parent;
            }

            var pricelist_items = _.filter(pricelist.items, function (item) {
                return (! item.product_tmpl_id || item.product_tmpl_id[0] === self.product_tmpl_id) &&
                       (! item.product_id || item.product_id[0] === self.id) &&
                       (! item.categ_id || _.contains(category_ids, item.categ_id[0])) &&
                       (! item.date_start || moment(item.date_start).isSameOrBefore(date)) &&
                       (! item.date_end || moment(item.date_end).isSameOrAfter(date));
            });

            var price = 0;
            _.find(pricelist_items, function (rule) {
                if (rule.min_quantity && quantity < rule.min_quantity) {
                    return false;
                }

                if (rule.base === 'pricelist') {
                    price = self.get_price(rule.base_pricelist, quantity);
                } else if (rule.base === 'standard_price') {
                    price = self.standard_price;
                }

                if (rule.compute_price === 'fixed') {
                    price = rule.fixed_price;
                    return true;
                } else if (rule.compute_price === 'percentage') {
                    price = price - (price * (rule.percent_price / 100));
                    return true;
                } else {
                    var price_limit = price;
                    price = price - (price * (rule.price_discount / 100));
                    if (rule.price_round) {
                        price = round_pr(price, rule.price_round);
                    }
                    if (rule.price_surcharge) {
                        price += rule.price_surcharge;
                    }
                    if (rule.price_min_margin) {
                        price = Math.max(price, price_limit + rule.price_min_margin);
                    }
                    if (rule.price_max_margin) {
                        price = Math.min(price, price_limit + rule.price_max_margin);
                    }
                }
                if (price != 0) {
                    return true;
                }

            });

            // This return value has to be rounded with round_di before
            // being used further. Note that this cannot happen here,
            // because it would cause inconsistencies with the backend for
            // pricelist that have base == 'pricelist'.
            return price;
        },
    });

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        is_paid: function(){
            if(this.pos.user.skip_payment){
                return true;
            }
            return _super_order.is_paid.call(this);
        },
        add_product: function (product, options) {
            // This block of code check the stock.
            var tagExists = $("#qty-tag" + product.id).length;
            var stockChecks = [
                !this.pos.config.wk_continous_sale,
                this.pos.config.wk_display_stock,
                tagExists,
                parseInt($("#qty-tag" + product.id).html()) <= self.pos.config.wk_deny_val,
            ]
            if (stockChecks.every(check => check)) {
                return self.pos.gui.show_popup('error',{
                    'title':  _t("Warning !!!!"),
                    'body': _t("("+product.display_name+")"+self.pos.config.wk_error_msg+"."),
                });
            };
            // End of modification.
            if(this._printed){
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});

            if(options.quantity !== undefined){
                line.set_quantity(options.quantity);
            }

            if(options.price !== undefined){
                line.set_unit_price(options.price);
            }

            //To substract from the unit price the included taxes mapped by the fiscal position
            this.fix_tax_included_price(line);

            if(options.discount !== undefined){
                line.set_discount(options.discount);
            }

            if(options.extras !== undefined){
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }

            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false){
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline){
                to_merge_orderline.merge(line);
                // The line bellow updates the pricelist value.
                to_merge_orderline.updateWithPricelist();
            } else {
                this.orderlines.add(line);
                // The line bellow updates the pricelist value.
                line.updateWithPricelist();
            }
            this.select_orderline(this.get_last_orderline());

            if(line.has_product_lot){
                this.display_lot_popup();
            }
            // This block of code updates de css and models.
            if (this.pos.config.wk_display_stock) {
                this.pos.chrome.wk_change_qty_css();
            };
            // End of modification.
        },
    });

    screens.set_pricelist_button.include({
        button_click: function () {
            var self = this;
            var partner = this.pos.get_client();
            var pricelists = self.pos.pricelists.slice();
            if (partner && partner.pricelist_ids.length){
                for(var i = 0, len = pricelists.length; i<len; i++){
                    if (!(partner.pricelist_ids.includes(self.pos.pricelists[i].id))) {
                        pricelists.splice(pricelists.indexOf(self.pos.pricelists[i]), 1);
                    }
                }
            }
            else if (partner && !(partner.pricelist_ids.length)){
                for(var i = 0, len = pricelists.length; i<len; i++){
                    if (self.pos.pricelists[i].id != partner.property_product_pricelist[0]) {
                        pricelists.splice(pricelists.indexOf(self.pos.pricelists[i]), 1);
                    }
                }
            }
            var pricelists = _.map(pricelists, function (pricelist) {
                return {
                    label: pricelist.name,
                    item: pricelist
                };
            });

            self.gui.show_popup('selection',{
                title: _t('Select pricelist'),
                list: pricelists,
                confirm: function (pricelist) {
                    var order = self.pos.get_order();
                    order.set_pricelist(pricelist);
                },
                is_selected: function (pricelist) {
                    return pricelist.id === self.pos.get_order().pricelist.id;
                }
            });
        },
    });

    screens.NumpadWidget.include({
        start: function() {
            this.state.bind('change:mode', this.changedMode, this);
            this.changedMode();
            this.$el.find('.numpad-backspace').click(_.bind(this.clickDeleteLastChar, this));
            this.$el.find('.numpad-minus').click(_.bind(this.clickSwitchSign, this));
            this.$el.find('.number-char').click(_.bind(this.clickAppendNewChar, this));
            this.$el.find('.mode-button').click(_.bind(this.clickChangeMode, this));
            var self = this;
            this.$el.find('.numpad-backspace').on('update_buffer',function(){
                return self.state.delete_last_char_of_buffer();
            });
        }
    });

    models.NumpadState = models.NumpadState.extend({
        delete_last_char_of_buffer: function() {
            if(this.get('buffer') === "")
            {
                if(this.get('mode') === 'quantity')
                    this.trigger('set_value','remove');
                else
                    this.trigger('set_value',this.get('buffer'));
            }
            else
            {
                var newBuffer = this.get('buffer').slice(0,-1) || "";
                this.set({ buffer: newBuffer });
                this.trigger('set_value',this.get('buffer'));
            }
        }
    });

    gui.Gui = gui.Gui.extend({
        show_screen: function(screen_name,params,refresh) {
            var self = this;
            self._super(screen_name,params,refresh);
            if (refresh) {
                self.pos.chrome.wk_change_qty_css();
            }
        }
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        template: 'Orderline',
        initialize: function(attr,options){
            this.option = options;
            this.comment = 0.0
            console.log("options");
            console.log(options);
            if (options.product){
                this.comment=parseInt($("#qty-tag" + options.product.id).html());
            }
            _super_orderline.initialize.call(this,attr,options);
        },
        updateWithPricelist () {
            const numpad = $('.numpad').block(), order = this.order;
            rpc.query({
                model: 'product.pricelist',
                method: 'get_product_price_rule_from_ui',
                args: [order.pricelist.id, this.product.id, this.quantity, (order.get_client() || {}).id]
            }).then((productPrices) => {
                const productPrice = productPrices[this.product.id];
                if (productPrice) {
                    this.set_unit_price(productPrice[0]);
                }
            }).always(() => numpad.unblock());
        },
        set_quantity: function(quantity) {
            var self = this;
            console.log('get_orderlines set quantity');
            console.log(self.pos.get('orders'));

            if(!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && isNaN(quantity)!=true && quantity!='' && parseFloat(self.comment)-parseFloat(quantity)<self.pos.config.wk_deny_val && self.comment !=0.0)
            {
                self.pos.gui.show_popup('error',{
                    'title':  _t("Warning !!!!"),
                    'body': _t("("+this.option.product.display_name+")"+self.pos.config.wk_error_msg+"."),
                });
                $('.numpad-backspace').trigger("update_buffer");

            }
            else
            {
                var wk_avail_pro = 0;
                if (self.pos.get('selectedOrder')) {
                    var wk_pro_order_line = (self.pos.get('selectedOrder')).get_selected_orderline();
                    if (!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && wk_pro_order_line) {
                        var wk_current_qty = parseInt($("#qty-tag" + (wk_pro_order_line.product.id)).html());
                        if (quantity == '' || quantity == 'remove') {
                            wk_avail_pro = wk_current_qty + wk_pro_order_line;
                        } else {
                            wk_avail_pro = wk_current_qty + wk_pro_order_line - quantity;
                        }

                        if (wk_avail_pro < self.pos.config.wk_deny_val && (!(quantity == '' || quantity == 'remove'))) {
                            self.pos.gui.show_popup('error', {
                                'title': _t("Warning !!!!"),
                                'body': _t("(" + wk_pro_order_line.product.display_name + ") " + self.pos.config.wk_error_msg + "."),
                            });
                        } else {

                            _super_orderline.set_quantity.call(this, quantity);
                        }
                    } else {
                        _super_orderline.set_quantity.call(this, quantity);
                    }
                    if (self.pos.config.wk_display_stock) {
                        self.pos.chrome.wk_change_qty_css();
                    }
                }
                 // This is the new else to fix bug
                else {
                        _super_orderline.set_quantity.call(this, quantity);
                }
            }
            this.updateWithPricelist();
        },
    });
});
