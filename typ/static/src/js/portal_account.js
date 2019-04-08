odoo.define('theme_typ.portal_account', function (require) {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $Edit_information = $('.all_shipping');

    if(!$Edit_information.length){
        return $.Deferred().reject("DOM doesn't contain any '.all_shipping' element.");
    }

    const Edit_information = Widget.extend({
        events: {
            'click .js_edit_address': function(event) {
                event.preventDefault();
                $(event.currentTarget).parents('div.account-information').find('form.hide').attr('action', '/my/contact/edit').submit();
            }
        }
    });

    $Edit_information.each(function(){
        const edit_information = new Edit_information();
        edit_information.attachTo($(this));
    });

});

