odoo.define('typ.models.extend', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;

    models.load_models({
        model: 'l10n_mx_edi.payment.method',
        fields: ['name'],
        loaded: function(self, l10n_mx_edi_payment_method){
            self.l10n_mx_edi_payment_method = l10n_mx_edi_payment_method;
        },
    });

    models.load_fields('res.partner', ['l10n_mx_edi_usage', 'l10n_mx_edi_payment_method_id']);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options){
            this.l10n_mx_edi_usage = this.l10n_mx_edi_usage || false;
            this.l10n_mx_edi_payment_method_id = this.l10n_mx_edi_payment_method_id || false;
            return _super_order.initialize.call(this, attributes, options);
        },
        init_from_JSON: function(json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.l10n_mx_edi_usage){
                this.l10n_mx_edi_usage = json.l10n_mx_edi_usage;
            } else {
                this.l10n_mx_edi_usage = this.get_client() ? this.get_client().l10n_mx_edi_usage : false;
            }
            if (json.l10n_mx_edi_payment_method_id){
                this.l10n_mx_edi_payment_mathod_id = json.l10n_mx_edi_payment_method_id;
            } else {
                this.l10n_mx_edi_payment_method_id = this.get_client() ? this.get_client().l10n_mx_edi_payment_method_id : false;
            }
            return res;
        },
        export_as_JSON: function() {
            var res = _super_order.export_as_JSON.call(this);
            res.l10n_mx_edi_usage = this.l10n_mx_edi_usage ? this.l10n_mx_edi_usage : false;
            res.l10n_mx_edi_payment_method_id = this.l10n_mx_edi_payment_method_id ? this.l10n_mx_edi_payment_method_id : false;
            return res;
        },
        set_usage: function(usage){
            this.assert_editable();
            this.l10n_mx_edi_usage = usage;
        },
        get_usage: function(){
            return this.l10n_mx_edi_usage;
        },
        set_payment_method: function(payment_method){
            this.assert_editable();
            this.l10n_mx_edi_payment_method_id = payment_method;
        },
        get_payment_method: function(){
            return this.l10n_mx_edi_payment_method_id;
        },
        set_client: function(client){
            if(client) {
                this.l10n_mx_edi_usage = client.l10n_mx_edi_usage;
                this.l10n_mx_edi_payment_method_id = client.l10n_mx_edi_payment_method_id;
            }
            return _super_order.set_client.apply(this, arguments);
        }
    });

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            this.usage_selection = {
                'G01': _t('Acquisition of merchandise'),
                'G02': _t('Returns, discounts or bonuses'),
                'G03': _t('General expenses'),
                'I01': _t('Constructions'),
                'I02': _t('Office furniture and equipment investment'),
                'I03': _t('Transportation equipment'),
                'I04': _t('Computer equipment and accessories'),
                'I05': _t('Dices, dies, molds, matrices and tooling'),
                'I06': _t('Telephone communications'),
                'I07': _t('Satellite communications'),
                'I08': _t('Other machinery and equipment'),
                'D01': _t('Medical, dental and hospital expenses.'),
                'D02': _t('Medical expenses for disability'),
                'D03': _t('Funeral expenses'),
                'D04': _t('Donations'),
                'D05': _t('Real interest effectively paid for mortgage loans (room house)'),
                'D06': _t('Voluntary contributions to SAR'),
                'D07': _t('Medical insurance premiums'),
                'D08': _t('Mandatory School Transportation Expenses'),
                'D09': _t('Deposits in savings accounts, premiums based on pension plans.'),
                'D10': _t('Payments for educational services (Colegiatura)'),
                'P01': _t('To define'),
            };
            return _super_posmodel.initialize.call(this,session,attributes);
        },
    });

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    screens.PaymentScreenWidget.include({
        // click_set_payment_method: function(){
        //     this.gui.show_screen('paymentmethodlist');
        // },
        click_set_usage: function(){
            // this.gui.show_screen('');
        },
        renderElement: function() {
            var self = this;
            this._super();
            // this.$('.js_set_payment_method').click(function(){
            //     self.click_set_payment_method();
            // });
            this.$('.js_set_usage').click(function(){
                self.click_set_usage();
            });
        },
        usage_changed: function() {
            var usage = this.pos.get_usage();
            this.$('.js_usage_name').text( usage ? '(' + usage + ')' + this.pos.usage_selection[usage] : _t('Usage'));
        },
    });

    // var PaymentMethodListScreenWidget = screens.ScreenWidget.extend({
    //     template: 'PaymentMethodListScreenWidget',

    //     back_screen: 'payment',

    //     show: function(){
    //         var self = this;
    //         this._super();

    //         this.renderElement();
    //         this.$('.back').click(function(){
    //             self.gui.back();
    //         });

    //         this.$('.next').click(function(){
    //             self.save_changes();
    //             self.gui.back();
    //         });
    //     },
    //     // save_changes: function(){
    //     // }
    // });
    // gui.define_screen({name:'paymentmethodlist', widget: PaymentMethodListScreenWidget});
});
