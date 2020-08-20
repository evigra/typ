odoo.define('typ.download_catalog', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $View_form = $('.oe_structure');
    const $Download_catalog = $('#download-catalog');

    if(!$View_form.length){
        return $.Deferred().Reject("DOM doesn't contain any '.oe_structure' element.");
    }

    const View_form = Widget.extend({
        events: {
            'click .has-form-download': (event) => {
                event.preventDefault();
                var $tgt = this.$(event.currentTarget);
                var link =  $tgt.attr("href");
                var catalog =  $tgt.closest("div").find('h4').text().trim();
                var $form = $Download_catalog.find('form');
                var $description = $Download_catalog.find('.o_download_description');
                $description.attr("value", catalog);
                $form.attr("data-success_download", link);
                $Download_catalog.modal()
            },
        }
    });

    $View_form.each(function(){
        const view_form = new View_form();
        view_form.attachTo($(this));
    });

    const Download_catalog = Widget.extend({
        events: {
            'click .o_website_form_send': (event) => {
                var link = this.$(event.currentTarget).closest("form").data("success_download");
                window.open(link,'_blank');
            }
        }
    });

    $Download_catalog.each(function(){
        const download = new Download_catalog();
        download.attachTo($(this));
    });

});
