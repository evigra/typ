odoo.define('theme_typ.stars', (require) => {
    'use strict';
    
    require('web.dom_ready');

    const Widget = require('web.Widget');
    const rpc = require('web.rpc');
    const ajax = require('web.ajax');
    const {qweb} = require('web.core');
    const {PortalChatter} = require('portal.chatter');

    const Stars = Widget.extend({
        template: 'typ_star_rating',
        xmlDependencies: [
            '/theme_typ/static/src/xml/templates.xml',
            '/theme_typ/static/src/xml/portal.xml',
            '/theme_typ/static/src/xml/rating.xml',
        ],
        init(parent){
            this._super.apply(this, arguments);
            this.options = parent.dataset;
        },
        _renderStars: function(){
            return this.$('.js_stars_content').html(qweb.render('typ_stars_collection', {widget: this}));
        },
        start(){
            this._super.apply(this, arguments);
            return rpc.query({
                route: '/mail/chatter_init',
                params: {...this.options, 'rating_include': true}
            }).then((result) => {
                if(result.rating_stats){
                    this.star_avarage = result.rating_stats.avg;
                    this.star_list = [1, 2, 3, 4, 5];
                    this._renderStars();
                }
            });
        }
    });

    PortalChatter.include({
        events: Object.assign(PortalChatter.prototype.events, {
            'click .js_show_comments': '_show_hide_comments'
        }),_show_hide_comments(ev){
            ev.preventDefault();
            this.$('.js_hidden_message').toggleClass('hidden');
        }
    });

    $('js_rating').each(function(){
        const stars = new Stars(this);
        stars.appendTo($(this));
    });

    return Stars;
});
