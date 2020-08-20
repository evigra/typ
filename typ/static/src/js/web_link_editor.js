odoo.define('typ.link_editor', function (require) {
    "use strict";

    var widget = require('web_editor.widget');
    var ajax = require('web.ajax');
    var {qweb} = require('web.core');
    ajax.loadXML(
        '/typ/static/src/xml/link_editor.xml', qweb
    );
    var AddForm = widget.LinkDialog.extend({

    });

});
