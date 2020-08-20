odoo.define('typ.download_catalog', (require) => {
    'use strict';

    require('web.dom_ready');

    const Widget = require('web.Widget');

    const $View_form = $('.oe_structure');

    if(!$View_form.length){
        return $.Deferred().Reject("DOM doesn't contain any '.oe_structure' element.");
    }

    const View_form = Widget.extend({
        events: {
            'click a': (event) => {
                event.preventDefault();
                var link =  $(event.currentTarget).attr("href");
                var catalog =  $(event.currentTarget).closest("div").find('h4').text().trim();
                var $form = $("#download-catalog").find('form');
                var $description = $("#download-catalog").find('.o_download_description');
                $description.attr("value", catalog);
                $form.attr("data-success_page", link);
                $("#download-catalog").modal()
            }
        }
    });

    $View_form.each(function(){
        const view_form = new View_form();
        view_form.attachTo($(this));
    });
});
