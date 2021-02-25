(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};
    openerp.jsonRpc('/customize_has_groups').done(function(res) {
        if (res == true){
            var liTags = document.getElementsByTagName("li");
            var searchText = "MY ENQUIRY";
            for (var i = 0; i < liTags.length; i++) {
                  if (liTags[i].outerText == searchText) {
                    liTags[i].style.display = "none"
                    break;
                  }
                }
            }

    })
})();

function belongs_to_all_groups(){

}