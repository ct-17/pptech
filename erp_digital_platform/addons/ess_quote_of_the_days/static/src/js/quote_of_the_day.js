(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};
    if ($('.quote-of-day-section').length >0) {
        openerp.jsonRpc('/get_quote_days_list').then(function (quote_data) {
            var quote_data_json = JSON.parse(quote_data)
            if (jQuery.isEmptyObject(quote_data_json) == false) {
                var snippet_quote = $('.snippet-quote')
                for (var i = 0; i < snippet_quote.length; i++) {
                    snippet_quote[i].children[0].innerText = "\"" + quote_data_json['quote'] +"\""
                    snippet_quote[i].children[0].innerHTML = "\"" + quote_data_json['quote'] +"\""
                    $('.author')[0].children[0].innerHTML = "—————  " + quote_data_json['autho']
                    // snippet_quote[i].children[1].setAttribute(
                    //    'src', 'data:image/png;base64,%s'.replace('%s', quote_data_json['img'])
                    // );
                }
            }
        })


    };


})();