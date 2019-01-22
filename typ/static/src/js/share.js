odoo.define('theme_typ.share_product', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $Share_product = $('.o_share_product');

    if(!$Share_product.length){
        return $.Deferred().Reject("DOM doesn't contain any '.o_share_product' element.");
    }

    const Share_product = Widget.extend({
        events: {
            'click .share-product-js': (event) => {
                event.preventDefault();
                var product_url = $(event.currentTarget).attr("data-value");
                $('<input>').appendTo('body').val(product_url).select();
                document.execCommand("copy");
                this.$('.copy-alert').removeClass('hidden');
            }
        }
    });

    $Share_product.each(function(){
        const share = new Share_product();
        share.attachTo($(this));
    });
});
