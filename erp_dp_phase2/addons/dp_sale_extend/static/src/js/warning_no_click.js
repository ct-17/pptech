openerp.dp_sale_extend = function (instance) {
    instance.web.form.FieldDatetime_warning_noclick = instance.web.form.FieldDatetime.extend({
        events: {
         'change': function()
            {
                 $("#ui-datepicker-div").hide()
            },
    },
        start: function bind() {
            this._super();
        }
    });

    instance.web.form.widgets.add(
        'warning_no_click', 'instance.web.form.FieldDatetime_warning_noclick'
    );
};