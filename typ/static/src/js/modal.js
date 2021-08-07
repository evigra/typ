odoo.define("type.modal", function () {
    /**
     * This module saves the screen position when a modal
     * its opened and scroll the view into that position
     * when closed.
     */

    if (!$.fn.modal) {
        return $.Deferred().reject("No Modal pluggin found.");
    }

    function getTarget() {
        var $oContent = $("html .o_web_client .o_content");
        return $oContent.css("overflow") == "visible" ? $(window) : $oContent;
    }

    var Modal = $.fn.modal.Constructor;

    var show = Modal.prototype.show;
    Modal.prototype.show = function () {
        this.lastScroll = getTarget().scrollTop();
        return show.apply(this, arguments);
    };

    var hide = Modal.prototype.hide;
    Modal.prototype.hide = function () {
        hide.apply(this, arguments);
        getTarget()[0].scrollTo({top: this.lastScroll, behavior: "smooth"});
    };
});
