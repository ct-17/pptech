document.addEventListener('readystatechange', evt => {
	console.log(document.readyState)
    if (document.readyState == "complete") {
        var t = setInterval(function loaded(){
			try{
					if(document.querySelectorAll("[data-menu=settings").length) {
						document.querySelectorAll("[data-menu=settings")[0].addEventListener("click", preference)
						clearInterval(t)
					}
				}
			catch (e) {
			}
		}, 500);
	}}, false);


function preference(){
	var t = setInterval(function loaded(){
			try{
					if(document.getElementsByClassName("oe_button oe_form_button oe_link").length){
						document.getElementsByClassName("oe_button oe_form_button oe_link")[0].addEventListener("click", changePassword)
						clearInterval(t)
					}
				}
			catch (e) {
			}
		}, 500);
}

function changePassword(){
	var t = setInterval(function loaded(){
			try{
					if(document.getElementsByClassName("modal-content openerp").length){
						notification_msg = "<p>Note: New Passwords must be at least <b>6</b> characters in length.</p>"
						$('.modal-body.oe_act_client').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + notification_msg + "</center></strong></div>");
						clearInterval(t)
					}
					var buttons = document.getElementsByClassName("oe_button oe_form_button")
					// for (var i = 0; i < buttons.length; i++) {
					//   if (buttons[i].outerText == "Change Password") {
					// 	buttons[i].addEventListener("click", validationCheck)
					//   }
					// }
				}
			catch (e) {
			}
		}, 500);
}


// function validationCheck(){
// 	if (document.getElementsByName("new_password")[0].value.length<6){
// 		alert('New Passwords must be at least 6 characters in length.');
// 		// event.stopPropagation()
// 		// event.preventDefault();
// 		// event.stopImmediatePropagation();
// 	}
// }
