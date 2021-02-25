jQuery(document).ready(function(){
	$('.home-banner').slick({
	  dots: false,
	  infinite: true,
	  arrows: false,
	  speed: 300,
	  slidesToShow: 1,
	  autoplay: true,
	});
	$('.super-deal .btn').magnificPopup({
		type: 'inline',
	});
});