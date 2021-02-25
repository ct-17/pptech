(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};

    if (document.getElementById("dropdown_pub_cat")) {
        openerp.jsonRpc('/dropdown_list/get_public_category')
            .then(function (data) {
                var pub_cat = JSON.parse(data);
                var dropdown = document.getElementById("dropdown_pub_cat");
                var opt = document.createElement('option');
                opt.appendChild( document.createTextNode('ALL PRODUCTS'));
                opt.value = 'ALL PRODUCTS';
                dropdown.appendChild(opt);
                for (var i=0; i<pub_cat['dropdown_select'].length; i++) {
                    var opt = document.createElement('option');
                    opt.appendChild( document.createTextNode(pub_cat['dropdown_select'][i]));
                    opt.value = pub_cat['dropdown_select'][i];
                    dropdown.appendChild(opt);
                }

            });
    }
})();