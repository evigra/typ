odoo.define('theme_typ.menu-icon', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $See_obj = $('.navbar-default');

    //Menu mobile button
    if(!$See_obj.length){
        return $.Defferred().Reject("DOM doesn't contain any '.navbar-default' element.");
    }

    const See_obj = Widget.extend({
        events: {
            'click .icon-menu-btn': (event) => {
                event.preventDefault();
                this.$('.navbar-collapse').toggleClass('hidden');
                this.$('body').toggleClass('cover-bg');
                this.$('.block-menu').toggleClass('hidden');
            },
            'click .icon-close-btn': (event) => {
                event.preventDefault();
                this.$('.navbar-collapse').toggleClass('hidden');
                this.$('.navbar-collapse').removeClass('collapse in');
                this.$('body').toggleClass('cover-bg');
                this.$('.block-menu').toggleClass('hidden');
            }
        }
    });

    $See_obj.each(function(){
        const see_obj = new See_obj();
        see_obj.attachTo($(this));
    });


    /* button search */
    const $See_search = $('#wrapwrap');

    if(!$See_search.length){
        return $.Defferred().Reject("DOM doesn't contain any '#wrapwrap' element.");
    }

    const See_search = Widget.extend({
        events: {
            'click .search-btn': (event) => {
                event.preventDefault();
                this.$('.to-hidden-menu').toggleClass('hidden');
                this.$('body').toggleClass('cover-bg');
                this.$('.block-body').toggleClass('hidden');
            }
        }
    });

    $See_search.each(function(){
        const see_search = new See_search();
        see_search.attachTo($(this));
    });

});
