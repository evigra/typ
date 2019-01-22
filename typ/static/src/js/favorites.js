odoo.define('theme_typ.favorites', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    const $Add_fav = $('.o_add_fav');

    if(!$Add_fav.length){
        return $.Deferred().Reject("DOM doesn't contain any '.o_add_fav' element.");
    }

    function remove_from_wishlist(prod_id) {
        rpc.query({
                model: 'user.wishlist',
                method: 'search_read',
                args: [[],['product_template_id']],

       }).then(function(data){
            for (var i = 0; i < data.length; i++) {
                var prod_temp_id = data[i].product_template_id[0];
                if (prod_temp_id === prod_id) {
                    var del_id = data[i].id;
                    rpc.query({
                        model: 'user.wishlist',
                        method: 'unlink',
                        args: [[del_id]],
                    });
                }
            }
       });
    }

    const Add_fav = Widget.extend({
        events: {
            'click .add-fav-js': (event) => {
                 // For Adding
                 if ($(event.currentTarget).hasClass('js_add_remove_wish_list_json') && $(event.currentTarget).hasClass('no-favorite-js')) {
                    event.preventDefault();
                    var product_id = $(event.currentTarget).attr('data-product-id');
                    ajax.jsonRpc("/add_to_wishlist/", 'call', {'product_id': product_id});
                    $(event.currentTarget).addClass('hidden');
                    this.$('.favorite-js').removeClass('hidden');
                    return;
                }
                // For Removing
                if ($(event.currentTarget).hasClass('js_add_remove_wish_list_json') && $(event.currentTarget).hasClass('favorite-js')) {
                    event.preventDefault();
                    var prod_id = $(event.currentTarget).attr('data-product-id');
                    remove_from_wishlist(prod_id);
                    $(event.currentTarget).addClass('hidden');
                    this.$('.no-favorite-js').removeClass('hidden');
                    return;
                }
            }
        }
    });

    $Add_fav.each(function(){
        const add_fav = new Add_fav();
        add_fav.attachTo($(this));
    });
});
