if (!odoo.defineCalled) {
    odoo.define('odoo_marketplace.icon_restriction', function (require) {
        'use strict';
        var ajax = require("web.ajax")
        $( document ).ready(function() {
            ajax.jsonRpc("/wk/check/mp/seller", 'call',{})
            .then(function (is_seller) {
                if(is_seller){
                    $('.o_ActivityMenuView, .MessagingMenuContainer').hide()

                }
            });
        });
    });
    odoo.defineCalled = true;
}

