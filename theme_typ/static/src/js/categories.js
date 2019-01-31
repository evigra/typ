odoo.define('theme_typ.categories', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $Show_categories = $('.nav-tabs');

    if(!$Show_categories.length){
        return $.Defferred().Reject("DOM doesn't contain any '.nav-tabs' element.");
    }

    var element_active="";
    var li_active="";
    var img_active="";

    const Show_categories = Widget.extend({
        events: {
            'mouseenter .categories_js': (event) => {
                this.$('a').removeClass('active');
                this.$(element_active).removeClass('active in');
                this.$(li_active).css("background-color", "white");
                this.$(img_active).addClass('hidden');

                element_active = $(event.currentTarget).attr("data-value");
                li_active = $(event.currentTarget).attr("index");

                element_active = "#"+element_active;
                img_active = "#img-category" +li_active;
                li_active = "#li"+li_active;

                this.$(element_active).addClass('active in');
                $(event.currentTarget).addClass("active");
                $(li_active).css("background-color", "#f5f5f5");
                $(img_active).removeClass('hidden');

            },
            'mouseenter .no_parent_js': () => {
                this.$('a').removeClass('active');
                this.$(element_active).removeClass('active in');
                this.$(li_active).css("background-color", "white");
                this.$(img_active).addClass('hidden');
            },
        }
    });

    $Show_categories.each(function(){
        const show_categories = new Show_categories();
        show_categories.attachTo($(this));
    });
});
