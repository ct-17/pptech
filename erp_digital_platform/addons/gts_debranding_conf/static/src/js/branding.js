openerp.gts_debranding_conf = function(instance) {
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

	instance.web.WebClient = instance.web.WebClient.extend({
	    init:function(parent, client_options){
	        this._super(parent,client_options);
	        this.set('title_part', {"zopenerp": $('#title_myconf').text()});
	    }
	});

	// handle default no_record message
	instance.web.ListView.include({
		no_result: function(){
			if (this.options.action && this.options.action.help){
			    str_title = "Elephas ERP"
				if (typeof(this.session.my_config) != 'undefined' && this.session.my_config.title){
                    str_title = this.session.my_config.title
				}
				this.options.action.help = this.options.action.help.replace('Odoo', str_title);
			}
			return this._super();

		}
	});

	instance.web_kanban.KanbanView.include({
		no_result: function(){
			if (this.options.action && (this.options.action.help || this.options.action.get_empty_list_help)){
				var help = this.options.action.help || this.options.action.get_empty_list_help;
				str_title = "Elephas ERP"
				if (typeof(this.session) != 'undefined' && typeof(this.session.my_config) != 'undefined' && this.session.my_config.title){
                    str_title = this.session.my_config.title
				}
				help = help.replace('Odoo', str_title);
				if (this.options.action.help){
					this.options.action.help = help;
				}
				else{
					this.options.action.get_empty_list_help = help;
				}
			}
			return this._super();
		}
	});

    instance.web.CrashManager = instance.web.CrashManager.extend({
        show_warning: function(error) {
            if (!this.active) {
                return;
            }
            if (error.data.exception_type === "except_osv") {
                error = _.extend({}, error, {data: _.extend({}, error.data, {message: error.data.arguments[0] + "\n\n" + error.data.arguments[1]})});
            }
            str_title = "ElephasERP"
            if (typeof(this.session) != 'undefined' && typeof(this.session.my_config) != 'undefined' && this.session.my_config.title){
                str_title = this.session.my_config.title
            }
            new instance.web.Dialog(this, {
                size: 'medium',
                title: str_title + "  " + (_.str.capitalize(error.type) || "Warning"),
                buttons: [
                    {text: _t("Ok"), click: function() { this.parents('.modal').modal('hide'); }}
                ],
            }, $('<div>' + QWeb.render('CrashManager.warning', {error: error}) + '</div>')).open();
        },
    });
    instance.web.RedirectWarningHandler = instance.web.RedirectWarningHandler.extend(instance.web.ExceptionHandler, {
        display: function() {
            var self = this;
            error = this.error;
            error.data.message = error.data.arguments[0];
            str_title = "Elephas ERP"
            if (typeof(this.session) != 'undefined' && typeof(this.session.my_config) != 'undefined' && this.session.my_config.title){
                str_title = this.session.my_config.title
            }
            new instance.web.Dialog(this, {
                size: 'medium',
                title: str_title + "  " + (_.str.capitalize(error.type) || "Warning"),
                buttons: [
                    {text: _t("Ok"), click: function() { self.$el.parents('.modal').modal('hide');  self.destroy();}},
                    {text: error.data.arguments[2],
                     oe_link_class: 'oe_link',
                     click: function() {
                        window.location.href='#action='+error.data.arguments[1];
                        self.destroy();
                    }}
                ],
            }, QWeb.render('CrashManager.warning', {error: error})).open();
        }
    });
};
