odoo.define('theme_typ.delete_product', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $Delete_product = $('.oe_cart');

    if(!$Delete_product.length){
        return $.Defferred().Reject("DOM doesn't contain any '.oe_cart");
    }

    const Delete_product = Widget.extend({
        events: {
            'click .js_delete_product': (event) => {
                event.preventDefault();
                $(event.currentTarget).closest('.row').find('.js_quantity').val(0).trigger('change');
            }
        }
    });

    $Delete_product.each(function(){
        const delete_product = new Delete_product();
        delete_product.attachTo($(this));
    });
});

