// Check jQuery available
if (typeof jQuery === 'undefined') { throw new Error('Theme JavaScript requires jQuery') }

// Check jQuery UI available
// if (typeof jQuery.ui === 'undefined') { throw new Error('Theme JavaScript requires jQuery UI') }

// Check Bootstrap JS plugins available
// if (typeof jQuery.fn.alert === 'undefined') { throw new Error('Theme JavaScript requires Bootstrap Alert plugin') }

// Check Backbone available
// if (typeof Backbone === 'undefined') { throw new Error('Theme JavaScript requires Backbone') }


+function ($) {
    'use strict';

    // LIBRARY OR OBJECT CODE HERE


    // Called when the HTML-Document is loaded and the DOM is ready, even if all the graphics haven’t loaded yet
    $(document).ready(function() {
        // CODE HERE
        // Hide required in field
        // setInterval(function(){ $("span.oe_form_field.oe_form_field_char.oe_form_required").removeClass("oe_form_required");
			// $(".oe_title.oe_left h1").find("span").addClass("custom_background");}, 50);

    });

    // Called when the complete page is fully loaded, including all frames, objects and images
    $(window).load(function() {

        // CODE HERE

    });

    openerp.blue_backend_theme_v8 = function(instance, local) {
        var _t = instance.web._t,
            _lt = instance.web._lt;
        var QWeb = instance.web.qweb;

        // Do not show company logo, show theme logo
        // instance.web.WebClient.include({
        //     update_logo: function() {
        //         var company = this.session.company_id;
        //         // var img = this.session.url('/web/binary/company_logo' + (company ? '?company=' + company : ''));
        //         // this.$('.oe_logo img').attr('src', '').attr('src', img);
        //         this.$('.oe_logo_edit').toggleClass('oe_logo_edit_admin', this.session.uid === 1);
        //     },
        // });
    }

}(jQuery);

