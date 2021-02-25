$(document).ready(function ()
	{
		
			
	 $("#sort_by").bind('change',function (ev) {
		  ev.preventDefault();
		  ev.stopPropagation();
		  $(this).closest("form").submit();     													     	
			 });
	 $("#filter_by_country").bind('change',function (ev) {
		  ev.preventDefault();
		  ev.stopPropagation();
		  $(this).closest("form").submit();
			 });

});
