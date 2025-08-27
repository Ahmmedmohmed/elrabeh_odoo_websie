odoo.define('odoo_marketplace.kanban_column',function(require){
"use strict";


    var KanbanColumn = require('web.KanbanColumn');
    var KanbanRenderer = require('web.KanbanRenderer');

    KanbanColumn.include({

        init: function (parent, data, options, recordOptions) {
            this._super(parent, data, options, recordOptions);
            if(data.context.no_archive == 1){
                this.has_active_field = false;
            }
        },
    });

});
