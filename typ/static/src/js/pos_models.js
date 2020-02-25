odoo.define('typ.models.extend', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    models.load_fields('res.partner', ['l10n_mx_edi_usage']);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes, options){
            this.l10n_mx_edi_usage = this.l10n_mx_edi_usage || false;
            return _super_order.initialize.call(this, attributes, options);
        },
        init_from_JSON: function(json) {
            var res = _super_order.init_from_JSON.apply(this, arguments);
            if (json.l10n_mx_edi_usage){
                this.l10n_mx_edi_usage = json.l10n_mx_edi_usage;
            } else {
                this.l10n_mx_edi_usage = this.get_client() ? this.get_client().l10n_mx_edi_usage : false;
            }
            return res;
        },
        export_as_JSON: function() {
            var res = _super_order.export_as_JSON.call(this);
            res.l10n_mx_edi_usage = this.l10n_mx_edi_usage ? this.l10n_mx_edi_usage : false;
            return res;
        },
        set_usage: function(usage){
            this.assert_editable();
            this.l10n_mx_edi_usage = usage;
        },
        get_usage: function(){
            return this.l10n_mx_edi_usage;
        },
        set_client: function(client){
            if(client) {
                this.l10n_mx_edi_usage = client.l10n_mx_edi_usage;
            }
            return _super_order.set_client.apply(this, arguments);
        },
        get_usage_byid: function(){
            var usages = this.pos.usage_selection;
            for(var i = 0; i < usages.length; i++){
                if( usages[i].id === this.l10n_mx_edi_usage){
                    return usages[i];
                }
            }
        },

    });

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            this.usage_selection = [
                {'id': 'G01', 'name': _t('Acquisition of merchandise')},
                {'id': 'G02', 'name': _t('Returns, discounts or bonuses')},
                {'id': 'G03', 'name': _t('General expenses')},
                {'id': 'I01', 'name': _t('Constructions')},
                {'id': 'I02', 'name': _t('Office furniture and equipment investment')},
                {'id': 'I03', 'name': _t('Transportation equipment')},
                {'id': 'I04', 'name': _t('Computer equipment and accessories')},
                {'id': 'I05', 'name': _t('Dices, dies, molds, matrices and tooling')},
                {'id': 'I06', 'name': _t('Telephone communications')},
                {'id': 'I07', 'name': _t('Satellite communications')},
                {'id': 'I08', 'name': _t('Other machinery and equipment')},
                {'id': 'D01', 'name': _t('Medical, dental and hospital expenses.')},
                {'id': 'D02', 'name': _t('Medical expenses for disability')},
                {'id': 'D03', 'name': _t('Funeral expenses')},
                {'id': 'D04', 'name': _t('Donations')},
                {'id': 'D05', 'name': _t('Real interest effectively paid for mortgage loans (room house)')},
                {'id': 'D06', 'name': _t('Voluntary contributions to SAR')},
                {'id': 'D07', 'name': _t('Medical insurance premiums')},
                {'id': 'D08', 'name': _t('Mandatory School Transportation Expenses')},
                {'id': 'D09', 'name': _t('Deposits in savings accounts, premiums based on pension plans.')},
                {'id': 'D10', 'name': _t('Payments for educational services (Colegiatura)')},
                {'id': 'P01', 'name': _t('To define')},
            ];
            return _super_posmodel.initialize.call(this,session,attributes);
        },
    });

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    screens.PaymentScreenWidget.include({
        click_set_usage: function(){
             this.gui.show_screen('usagelist');
        },
        renderElement: function() {
            var self = this;
            this._super();
            this.$('.js_set_usage').click(function(){
                self.click_set_usage();
            });
        },
        // usage_changed: function() {
        //     var usage = this.pos.get_usage();
        //     this.$('.js_usage_name').text( usage ? '(' + usage + ')' + this.pos.usage_selection[usage] : _t('Usage'));
        // },
    });

    var UsageListScreenWidget = screens.ScreenWidget.extend({
        template: 'UsageListScreenWidget',

        back_screen: 'payment',

        show: function(){
            var self = this;
            this._super();

            this.renderElement();
            this.old_usage = this.pos.get_order().get_usage();

            this.$('.back').click(function(){
                self.gui.back();
            });

            this.$('.next').click(function(){
                self.save_changes();
                self.gui.back();
            });

            this.render_list(this.pos.usage_selection);

            this.$('.client-list-contents').delegate('.client-line','click',function(event){
                self.line_select(event,$(this),$(this).data('id'));
            });

            var search_timeout = null;

            if(this.pos.config.iface_vkeyboard && this.chrome.widget.keyboard){
                this.chrome.widget.keyboard.connect(this.$('.searchbox input'));
            }

            this.$('.searchbox input').on('keypress',function(event){
                clearTimeout(search_timeout);

                var searchbox = this;

                search_timeout = setTimeout(function(){
                    self.perform_search(searchbox.value, event.which === 13);
                },70);
            });

            this.$('.searchbox .search-clear').click(function(){
                self.clear_search();
            });
        },
        find_usage_byname: function(query){
            var usages = [];
            for(var i = 0; i < this.pos.usage_selection.length; i++){
                var usage = this.pos.usage_selection[i];
                if( usage.name.toLowerCase().search(query.toLowerCase()) !== -1 ){
                    usages.push(usage);
                }
            }
            return usages;
        },
        find_usage_byid: function(id){
            for(var i = 0; i < this.pos.usage_selection.length; i++){
                if( this.pos.usage_selection[i].id === id){
                    return this.pos.usage_selection[i];
                }
            }
        },
        perform_search: function(query, associate_result){
            var usages = [];
            if(query){
                usages = this.find_usage_byname(query);
                if ( associate_result && usages !== []){
                    this.new_usage = usages[0];
                    this.save_changes();
                    this.gui.back();
                }
                this.render_list(usages);
            }else{
                usages = this.pos.usage_selection;
                this.render_list(usages);
            }
        },
        clear_search: function(){
            var usages = this.pos.usage_selection;
            this.render_list(usages);
            this.$('.searchbox input')[0].value = '';
            this.$('.searchbox input').focus();
        },
        save_changes: function(){
            var order = this.pos.get_order();
            if( this.has_usage_changed() ){
                order.set_usage(this.new_usage);
            }
        },
        render_list: function(usages){
            var contents = this.$el[0].querySelector('.client-list-contents');
            contents.innerHTML = "";
            for(var i = 0, len = usages.length; i < len; i++){
                var usage = usages[i];
                var usageline_html = QWeb.render('UsageLine',{widget: this, usage:usages[i]});
                var usageline = document.createElement('tbody');
                usageline.innerHTML = usageline_html;
                usageline = usageline.childNodes[1];
                if( usage.id === this.old_usage ){
                    usageline.classList.add('highlight');
                }else{
                    usageline.classList.remove('highlight');
                }
                contents.appendChild(usageline);
            }
        },
        has_usage_changed: function(){
            if( this.old_usage && this.new_usage ){
                return this.old_usage !== this.new_usage;
            }else{
                return !!this.old_usage !== !!this.new_usage;
            }
        },
        toggle_save_button: function(){
             var $button = this.$('.button.next');
             if( this.new_usage ){
                if( !this.old_usage ){
                    $button.text(_t('Set Usage'));
                }else{
                    $button.text(_t('Change Usage'));
                }
             }else{
                 $button.text(_t('Deselect Usage'));
             }
             $button.toggleClass('oe_hidden',!this.has_usage_changed());
        },
        line_select: function(event,$line,id){
            var usage = this.find_usage_byid(id);
            this.$('.client-list .lowlight').removeClass('lowlight');
            if ( $line.hasClass('highlight') ){
                $line.removeClass('highlight');
                $line.addClass('lowlight');
                this.new_usage = null;
                this.toggle_save_button();
            }else{
                this.$('.client-list .highlight').removeClass('highlight');
                $line.addClass('highlight');
                this.new_usage = usage.id;
                this.toggle_save_button();
            }
        },
    });
    gui.define_screen({name:'usagelist', widget: UsageListScreenWidget});
});
