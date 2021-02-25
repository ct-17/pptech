(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};

})
jQuery(document).ready(function(){
    var access_myenquiry = JSON.parse(localStorage.getItem('access_buytaxfree')) || 0;


	if($("#newsletter-popup").length >0 && access_myenquiry == 0){
		jQuery(window).load(function(){
		    jQuery.magnificPopup.open({
		        items: {src: '#newsletter-popup'},type: 'inline'},0);

	    });
	// 	$('#enter21').magnificPopup({
	// 	type: 'inline',
	// 	preloader: false,
	// });

    }

    $(document).on("click", "li.country-data", function(e){
	        console.log("work");
	        var liValue = $(this).html();
	        console.log(liValue);
	        $("#country-data").val(liValue);
	});



	$('#subscribe_button').on("click",  function(e){
	        console.log("work");
 	        openerp.jsonRpc('/write_newsletter_member', 'call', {
                                'name': $("input[id='email_subscribe']").val(),
                                  context: _.extend(openerp.website.get_context())
                            })
                .then(function (result){
                    jQuery.magnificPopup.close()


                })
	});
    access_myenquiry += 1;
    localStorage.setItem('access_buytaxfree', access_myenquiry);

    var check_prompt = setInterval(myTimer, 300);
    function myTimer(){
        if (document.getElementById('newsletter-popup') && !document.getElementById('newsletter-popup').classList.contains('mfp-hide')){
            $('div').click(function(e) {
                e.stopPropagation();
            });
            $("body").on("keyup", function(e){
                if (e.which === 27){
                    return false;
                }
            });
            clearInterval(check_prompt);
        }
    }
});