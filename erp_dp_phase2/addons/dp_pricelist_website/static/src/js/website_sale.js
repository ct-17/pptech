$(document).ready(function ()  {
    'use strict';
    var website = openerp.website,
        _t = openerp._t
    $('.oe_website_sale').each(function () {
        var cart_website_sale = this;

        $(cart_website_sale).find(".oe_cart input.js_quantity").on('change', function (){
            var $input = $(this);
            // if ($input.data('update_change')) {
            //
            // }

        })


    })
})