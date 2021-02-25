$(window).on('load', function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};

    // if ($('#stock_level').length > 0){
    //     if ($('#stock_level').find('img').length > 0 &&  $('#stock_level').find('img')[0].title == 'RED'){
    //         var _t = openerp._t;
    //         var notification_msg_insufficient = _t("There is insufficient stock to fulfill your request. Please consider the products suggested in");
    //         var you_may_also = _t("YOU MAY ALSO BE INTERESTED IN THESE");
    //         if (!document.getElementById('myAlert')) {
    //                // alert("This product is running low. \n\n" +
    //                //     "You may like to consider the product in \n" +
    //                //     "'YOU MAY ALSO BE INTERESTED IN THESE' section (below)." )
    //                 $('.js_sale').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + notification_msg_insufficient + "<br>" + "<div style='color:#000000'>" + "\"" + you_may_also + "\"" + " (BELOW)" + "</div></center></strong></div>");
    //             }
    //         } else {
    //             // $('.js_sale').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + notification_msg + "</center></strong></div>");
    //         }
    //     }
})