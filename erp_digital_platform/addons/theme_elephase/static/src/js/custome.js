jQuery(function($){
	jQuery(document).ready(function(){
var wid = $(window).width();
       if (wid <= 767)
       {
         $(".left-sidebar h3").click(function () {
			$(".shop-menu-list").slideToggle("slow");
		});
       }
	    });
});	   

jQuery(document).ready(function(){
	$(".button-menu").click(function () {
        $(".menu-part").slideToggle("slow");
		$(this).toggleClass('active');
    });
	$('.home-banner').slick({
	  dots: false,
	  infinite: true,
	  arrows: false,
	  speed: 300,
	  slidesToShow: 1,
	  autoplay: true,
	});
	
// 	jQuery(window).load(function(){
// 	    jQuery.magnificPopup.open({
// 	        items: {src: '#newsletter-popup'},type: 'inline'},0);
// 	    
//     });
	//$('.super-deal .btn').magnificPopup({
	//	type: 'inline',
	//});
// 	
// 	$("#enter21").click(function(){
// 	    jQuery.magnificPopup.close();
// 	}); 
	
});

$(document).ready(function () {
    $('#o_shop_collapse_category').on('click', '.fa-chevron-right',function(){
        $(this).parent().siblings().find('.fa-chevron-down:first').click();
        $(this).parents('li').find('ul:first').show('normal');
        $(this).toggleClass('fa-chevron-down fa-chevron-right');
    });

    $('#o_shop_collapse_category').on('click', '.fa-chevron-down',function(){
        $(this).parent().find('ul:first').hide('normal');
        $(this).toggleClass('fa-chevron-down fa-chevron-right');
    });
});
