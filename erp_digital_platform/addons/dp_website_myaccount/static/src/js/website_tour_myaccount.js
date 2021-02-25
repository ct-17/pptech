(function () {
    'use strict';

    var _t = openerp._t;
    var website = openerp.website;

    website.ready().done(function() {
    openerp.Tour.register({
        id: 'myenquiry',
        name: _t("My Enquiry"),
        path: '/myenquiry',

        steps: [
            {
                title:     _t("Welcome to your Enquiry"),
                content:   _t("This guide will help you to review your order"),
                popover:   { next: _t("Start Tutorial"), end: _t("Skip It") },
            },

            {
                element:   '#order_link',
                placement: 'left',
                title:     _t("Review Quotation"),
                content:   _t("Click here to view Quotation"),
                popover:   { fixed: true },
            },

            {
                waitFor:   '.js_publish_management button.js_publish_btn.btn-success:visible',
                title:     _t("Congratulations"),
                content:   _t("Congratulations! You just created and published your first product."),
                popover:   { next: _t("Close Tutorial") },
            },
        ]
    });
    $('#myenquiry').each( function() {
        var access_myenquiry = JSON.parse(localStorage.getItem('access_myenquiry_time')) || 0;
        var menu = $('#help-menu');
        var myenquire_tul = window.openerp.Tour.tours.myenquiry;
        var $menuItem = $($.parseHTML('<li><a href="#">'+myenquire_tul.name+'</a></li>'));
        $menuItem.click(function () {
                        openerp.Tour.run(myenquire_tul.id);
                    });
                    menu.append($menuItem);
        localStorage.setItem('access_myenquiry_time', access_myenquiry);
        if ($('#myenquiry').find('table').length > 0){
            if (access_myenquiry == 0){
                openerp.Tour.run(myenquire_tul.id)
            }
            access_myenquiry += 1;
            localStorage.setItem('access_myenquiry_time', access_myenquiry);
        }



    })
    });


//      window.openerp.website.EditorBar.include({
//         tours: [],
//         start: function () {
//             var self = this;
//             var menu = $('#help-menu');
//             _.each(window.openerp.Tour.tours, function (tour) {
//                 if (tour.mode === "test") {
//                     return;
//                 }
//                 var $menuItem = $($.parseHTML('<li><a href="#">'+tour.name+'</a></li>'));
//                 $menuItem.click(function () {
//                     openerp.Tour.run(tour.id);
//                 });
//                 menu.append($menuItem);
//             });
//             return this._super();
//         }
// });

}());
