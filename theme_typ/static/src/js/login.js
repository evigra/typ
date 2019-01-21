odoo.define('theme_typ.login', function (require) {
    "use strict";

    var Widget = require('web.Widget'),
        /* core = require('web.core'),
        website = require('website.website'), */
        ajax = require('web.ajax');

    require('web.dom_ready');

    var submitLogIn = Widget.extend({
        events: {
            'click .submit-log-in': 'onClick',
            'click .submit-sign-up': 'onClick',
        },
        init: function(parent) {
            this._super(parent);
        },
        onClick: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var form = this.$el,
                action = form.data('action'),
                values = this._get_form_values(form);
            ajax.post(action, values).then(function(result){
                this.js_result = $.parseJSON(result);
                if (this.js_result.login_success) {
                    if ('crm_name' in values) {
                        values.contact_name = values.name;
                        values.name = values.crm_name;
                        values.email_from = values.login;
                        /* ajax.post('/website_form/crm.lead', values).then(function(){
                        }); */
                    }
                    if(this.js_result.alert_mail_confirmation){
                        var value = true, self = this;
                        $('.modal-login').modal('hide');
                        $('.modal-login').on('hidden.bs.modal', function () {
                            if (value) {
                                $('#mail-from-signup').html(self.js_result.login);
                                $('#confirm_email_id').modal('show');
                                value = false;
                            }
                    });
                    }else{
                        $(location).attr('href', '/');
                    }
                } else {
                    this.error_msg = form.find('.login-modal-error, .signup-modal-error');
                    this.error_msg.replaceWith('<p class="alert alert-danger login-modal-error mb0">'+ this.js_result.error +'</p>');
                }
            });
        },
        _get_form_values(form) {
            var form_values = {};
            this.fields = form.serializeArray();
            _.each(this.fields, function(input){
                if (input.name in form_values) {
                    if (Array.isArray(form_values[input.name])) {
                        form_values[input.name].push(input.value);
                    } else {
                        form_values[input.name] = [form_values[input.name], input.value];
                    }
                }
                if (input.value !== '') {
                    form_values[input.name] = input.value;
                }
            });
            return form_values;
        }
    });

    /* var changeModal = Widget.extend({
        events: {
            'click .change-modal-login': 'onClick',
        },
        init: function(parent, options) {
            this._super(parent);
        },
        onClick: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var modal_login = this.$el,
                id_show = modal_login.data('modal-id'),
                value = true;
            modal_login.modal('hide');
            modal_login.on('hidden.bs.modal', function () {
                if (value) {
                    $('#'+id_show).modal('show');
                    value = false;
                }
            });
        }
    }); */

    if(!$('.modal_form_login, .modal_form_signup, .modal-login, .oe_login_form').length) {
        return $.Defferred().reject('DOM does not contain log in form');
    }
    $('.modal_form_login, .modal_form_signup, .oe_login_form').each(function(){
        var $elem = $(this);
        var button = new submitLogIn(null, $elem.data());
        button.attachTo($elem);
    });
    /* $('.modal-login').each(function(){
        var $elem = $(this);
        var btn_change = new changeModal(null, $elem.data());
        btn_change.attachTo($elem);
    }); */
    return submitLogIn;
});
