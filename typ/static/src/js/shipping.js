odoo.define('theme_typ.shipping_address', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');
    var ajax = require('web.ajax');

    const $Change_address = $('.all_shipping');

    if(!$Change_address.length){
        return $.Defferred().Reject("DOM doesn't contain any '.all_shipping' element.");
    }

    const Change_address = Widget.extend({
        events: {
            'click .change_address_js': (event) => {
                event.preventDefault();
                $('.address').removeClass('fa-star address-selected');
                $('.address').addClass('fa-star-o change_address_js');
                $('.address').find('span').addClass('hidden');
                $(event.currentTarget).removeClass('fa-star-o change_address_js');
                $(event.currentTarget).addClass('fa-star address-selected');
                $(event.currentTarget).find('span').removeClass('hidden');

                $('.no-delete-address').removeClass('hidden no-delete-address').addClass('delete-address');

                var address_pret = $(event.currentTarget).attr("data-value");
                address_pret = "#delete-btn" + address_pret;

                $(address_pret).addClass('hidden no-delete-address').removeClass('delete-address');

                var $form = $('div.one_kanban').find('form.hide');
                $.post($form.attr('action'), $form.serialize()+'&xhr=1');
            },
            'click .delete_address_js': (event) => {
                event.preventDefault();
                var address_id = $(event.currentTarget).attr('data-address-id');
                ajax.jsonRpc("/delete-address/", 'call', {'address_id': address_id});
                $(event.currentTarget).parents('div.account-information').addClass('hidden');
           }
        }
    });

    $Change_address.each(function(){
        const change_address = new Change_address();
        change_address.attachTo($(this));
    });
});
