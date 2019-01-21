odoo.define('theme_.login_validator', function(require){
    "use strict";

    var Widget = require('web.Widget');
    require('web.dom_ready');

    var LoginValidator = Widget.extend({
        events: {
            'click button[type="submit"]': 'onClick',
        },
        init: function(parent) {
            this._super(parent);
        },
        onClick: function(ev) {
            if(!this._verify_fields(this.$el)){
                ev.preventDefault();
                ev.stopPropagation();
            }
        },
        _verify_fields(form) {
            let invalid = false;
            for (const el of form[0].elements){
                const $el = $(el).parent();
                if(el.checkValidity()){
                    $el.removeClass('has-error');
                }else{
                    invalid = true;
                    $el.addClass('has-error');
                }
            }
            return !invalid;
        }
    });

    var forms = $('.oe_website_login_container .oe_login_form, .oe_website_login_container .oe_reset_password_form, .oe_website_login_container .oe_signup_form');
    if(!forms.length) {
        return $.Defferred().reject('DOM does not contain a log in form page.');
    }
    forms.each(function(){
        const form = new LoginValidator(null);
        form.attachTo($(this));
    });

    return LoginValidator;
});
