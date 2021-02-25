openerp.gts_discount = function(instance) {
    var _t = instance.web._t,
    _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.ListView.List.include({
    	render: function () {
    		this.$current.empty().append(
    	            QWeb.render('ListView.rows', _.extend({
    	                    render_cell: function () {
    	                        return self.render_cell.apply(self, arguments); }
    	                }, this)));
    	    this.pad_table_to(4);
            //this.$current.find("td[data-field='name']:contains('Discount'):eq(0)").parent().css({'display': 'none'});

    	    if (this.$current.find("td[data-field='price_unit']") && this.$current.find("td[data-field='price_unit']").length !== 0)
	    	{	
    	    	for (var i=0 ;i < this.$current.find("td[data-field='price_unit']").length; i++){
    	    		var x = $(this.$current.find("td[data-field='price_unit']")[i]).text();
    	            var y = $(this.$current.find("td[data-field='name']")[i]).text()
    	    		if (parseFloat(x) < 0 && y === 'Discount')
    	    	    {
    	    			$(this.$current.find("td[data-field='name']")[i].parentElement).remove();
    	    	     } 
    	    	}
	    	 }
    	},
    })
};