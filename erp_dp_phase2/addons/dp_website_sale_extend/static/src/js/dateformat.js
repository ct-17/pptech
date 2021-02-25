$(document).ready(function () {
    $('[data-toggle="datepicker"]').datepicker( "option", "dateFormat", "dd/mm/yy" );

    $(function() {
        $('#typedate').on('change', function (e){
            var date = $('#typedate').datepicker('getDate');
            convert_datetime(date, 2, 'dd/mm/yyyy', '#estimated_departure_id')
            // date2.setDate(date2.getDate()+2);
            // var date = date2.getDate(); var month = date2.getMonth()+1; var year = date2.getFullYear()
            // var departure_date = date + '/' + month+ '/' + year
            // $('#estimated_departure_id').datepicker('setDate', departure_date);

		 	$('.datepicker-container').addClass("datepicker-hide");
		 	if(document.getElementsByClassName('datepicker-container')[0]){
				document.getElementById('typedate').addEventListener('click',function() {
				    var datepicker_container = $('.datepicker-container')
                    for (var i=0;i<datepicker_container.length;i++){
                        var left_string = datepicker_container[i].style.left
                        if (left_string.split("px")[0]< $(window).width()/2){
                           $($('.datepicker-container')[i]).removeClass("datepicker-hide");
                        }
                    }
				})
			}
		 	if (document.getElementById('typedate').value!=''){
                var typedate = document.getElementById('typedate').value.split('/')
                var typedate_date = new Date(typedate[2],typedate[1]-1, typedate[0])
                $('#estimated_departure_id').datepicker('setStartDate', typedate_date);
            }
        });

        $('#estimated_departure_id').on('change', function (e){
            var date = $('#estimated_departure_id').datepicker('getDate');
		 	$('.datepicker-container').addClass("datepicker-hide");
		 	if(document.getElementsByClassName('datepicker-container').length > 1){
                if(document.getElementsByClassName('datepicker-container')[1]){
                    document.getElementById('estimated_departure_id').addEventListener('click',function() {
                        var datepicker_container = $('.datepicker-container')
                        for (var i=0;i<datepicker_container.length;i++){
                            var left_string = datepicker_container[i].style.left
                            if (left_string.split("px")[0] > $(window).width()/2){
                                $($('.datepicker-container')[i]).removeClass("datepicker-hide");
                            }
                        }
                    })
                }
			}
        });

        var today = new Date();
		var today_date = today.getDate() + '/'+(today.getMonth()+1)+'/' + today.getFullYear();
        $('[data-toggle="datepicker"]').datepicker('setStartDate', today);
        if(document.getElementById('estimated_departure_id')){
            document.getElementById('estimated_departure_id').addEventListener('click',function() {
                try{
		 	        // $('.datepicker-container')[.addClass("datepicker-hide");
                }
                catch (e) {
                    null;
                }
            })
        }
    });


function convert_datetime(date, diff_day=0, format, id_update){
    // """ this function is common to convert date time"""
    date.setDate(date.getDate()+ diff_day);
    var day = date.getDate();
    var month = date.getMonth()+1;
    var year = date.getFullYear()
    if (format == 'dd/mm/yyyy'){
        var new_date_format = day + '/' + month+ '/' + year;
    }
    else if (format == 'dd-mm-yyyy'){
        var new_date_format = day + '-' + month+ '-' + year;

    }
    $(id_update).datepicker('setDate', new_date_format);
}
});