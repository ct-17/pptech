function show_hide_buttons () {

    // Todo: this function does not work
    // $('#edit_button1').show();
    $('#submit_button1').hide();
    // $('#edit_button2').show();
    $('#submit_button2').hide();
    // $('#edit_button3').show();
    $('#submit_button3').hide();
    // $('#chandler_id1').hide();
    $('#chandler_autocomplete_id1').show();
    // $('#chandler_id2').hide();
    $('#chandler_autocomplete_id2').show();
    // $('#chandler_id3').hide();
    $('#chandler_autocomplete_id3').show();
    // $('#chandler1_name_user_input_id').hide();
    // $('#chandler1_email_user_input_id').hide();
    // $('#chandler2_name_user_input_id').hide();
    // $('#chandler2_email_user_input_id').hide();
    // $('#chandler3_name_user_input_id').hide();
    // $('#chandler3_email_user_input_id').hide();
    // $('#chandler1_prev_id').hide();
    // $('#chandler2_prev_id').hide();
    // $('#chandler3_prev_id').hide();
    // $('#chandler1_prefer_id').hide();
    // $('#chandler2_prefer_id').hide();
    // $('#chandler3_prefer_id').hide();
    // $('#submit_btn1_num').hide();
    // $('#submit_btn2_num').hide();
    // $('#submit_btn3_num').hide();
    $('#shipping_agent_name_id').hide();
    $('#shipping_agent_contact_id').hide();
    $('#shipping_agent_cr_number_id').hide();
    $('#vessel_name_id').hide();
    $('#imo_number_id').hide();
    $('#vessel_type_select_id').hide();
    $('#vessel_nrt_id').hide();
    $('#vessel_flag_id').hide();
    $('#vessel_crew_id').hide();
    // $('#shipping_agent_select_id').hide();
};


/**
 * Return if a particular option exists in a <select> object
 * @param {String} needle A string representing the option you are looking for
 * @param {Object} haystack A Select object
*/
function optionExists ( needle, haystack )
{
    var optionExists = false,
        optionsLength = haystack.length;

    while ( optionsLength-- )
    {
        if ( haystack.options[ optionsLength ].value === needle )
        {
            optionExists = true;
            break;
        }
    }
    return optionExists;
}

function close_create_new_shipping_agent(ev) {
    $('#modal_create_new_shipping_agent').remove();
    for (i=0; i<document.getElementsByClassName('modal-backdrop fade in').length; i++ ) {
        document.getElementsByClassName('modal-backdrop fade in')[i].removeAttribute('class')
    }
}

function hide_show_create_and_edit_shipping_agent() {
    if (document.getElementById('ship_agent_select').value === 'CREATE..') {
        var ship_agent = $('#ship_agent_select').val()
        create_new_shipping_agent(true, ship_agent);
    }
}

function create_new_shipping_agent(flag, ship_agent) {
    if (flag && !document.getElementById('modal_create_new_shipping_agent')) {
        var website = openerp.website;
        website.openerp_website = {};
        var $form = $('.oe_website_sale');
        openerp.jsonRpc('/create_new_shipping_agent', 'call', {
               context: _.extend({'open_shipping_agent_form': 'True', 'shipping_agent_name': ship_agent}, openerp.website.get_context())
            }).then(function (modal) {
            self = this;

            var $modal = $(modal);
            if (!document.getElementById('modal_create_new_shipping_agent')) {
                $modal.appendTo($form)
                .modal()
                .on('hidden.bs.modal', function () {
                    $(this).remove();
                });

                $('.oe_website_sale').fadeIn();
                $modal.fadeOut();

                $('#create_new_shipping_agent_button').click(function(ev) {
                    if ($("#shipping_agent_name_id").val() === "") {
                        var msg = "Please fill up the mandatory fields in asterisk (*)";
                        var required_fields = document.getElementById('modal_create_new_shipping_agent').querySelectorAll('[required="required"]'),i;
                        var mandary_field_empty = false
                        for (i = 0; i < required_fields.length; ++i) {
                            if (required_fields[i].value==""){
                                required_fields[i].classList.add('has-error_myaccount')
                                mandary_field_empty = true;
                            }
                            else{
                                if(required_fields[i].classList.contains('has-error_myaccount')){
                                    required_fields[i].classList.remove('has-error_myaccount')
                                }
                            }
                        }
                        if (mandary_field_empty){
                            if (!document.getElementById('create_shipping_agent_myAlert1')){
                                var msg = '<p>Please fill up the mandatory fields in asterisk (*)</p>\n';
                                var delayInMilliseconds = 100;
                                setTimeout(function() {
                                    $('#fill_mandatory_fields_create_shipping_agent').append("<div id ='create_shipping_agent_myAlert1' class ='alert alert-danger'><div id='noshippingagentname'><strong><center>" + msg + "</center></strong></div></div>");
                                    $('#create_new_shipping_agent_button').parent().prepend("<div id ='create_shipping_agent_myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                                }, delayInMilliseconds);
                            }
                            return false;
                        }
                        else{
                            $('.has-error_myaccount').removeClass( "has-error_myaccount" )
                            $('#create_shipping_agent_myAlert1').remove()
                            $('#create_shipping_agent_myAlert2').remove()
                        }
                        ev.stopPropagation();
                    } else {
                         openerp.jsonRpc('/create_new_shipping_agent', 'call', {
                            'shipping_agent_name': $modal.find("input[name='shipping_agent_name']").val(),
                            'shipping_agent_contact': $modal.find("input[name='shipping_agent_contact']").val(),
                            'shipping_agent_cr_number': $modal.find("input[name='shipping_agent_cr_number']").val(),
                             context: _.extend(openerp.website.get_context())
                        }).then(function (result) {
                            if (result == true){
                                $("#ship_agent_select").val($('#shipping_agent_name_id').val());
                                $("#new_vessel_flag").val("1");
                                $('#modal_create_new_shipping_agent').remove();
                                for (i=0; i<document.getElementsByClassName('modal-backdrop fade in').length; i++ ) {
                                    document.getElementsByClassName('modal-backdrop fade in')[i].removeAttribute('class')
                                }
                            }
                            else {
                                var msg1 = "Shipping Agent Name already exists in the database<br>Please use another name!";
                                if (document.getElementById("fill_mandatory_fields")) {
                                    if (document.getElementById('myAlert1')) {
                                        if (document.getElementById('cannotcreateshippingagent')) {
                                            document.getElementById('cannotcreateshippingagent').innerHTML = "<strong><center>" + msg1 + "</center></strong>"
                                        } else {
                                            document.getElementById('myAlert1').innerHTML = document.getElementById('myAlert1').innerHTML + "<div id='cannotcreateshippingagent'><strong><center>" + msg1 + "</center></strong></div>"
                                        }
                                    } else {
                                        $('#fill_mandatory_fields_create_shipping_agent').append("<div id ='myAlert1' class ='alert alert-danger'><div id='cannotcreateshippingagent'><strong><center>" + msg1 + "</center></strong></div></div>");
                                    }
                                }
                            }
                         })
                     }
                });
            }
        });
    }
}


function autocomplete(inp, arr, context={}) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var prev_leng = arr.length;
  var must_show_leng = 0;
  if ('must_show' in context) {
     arr = arr.filter(function(e) { return e !== 'OTHERS' })
      arr = arr.concat(context['must_show']);
      // var count = 0;
      //   for(var i = 0; i < arr.length; ++i){
      //       if(arr[i] == 'OTHERS')
      //           count++;
      //   }
        // arr = arr.concat(String(count));
      must_show_leng = arr.length;

  }
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      for (i = 0; i < prev_leng; i++) {
        /*check if the item starts with the same letters as the text field value:*/
        if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
          /*create a DIV element for each matching element:*/
          b = document.createElement("DIV");
          /*make the matching letters bold:*/
          b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
          b.innerHTML += arr[i].substr(val.length);
          /*insert a input field that will hold the current array item's value:*/
          b.innerHTML += '<input type="hidden" value="' + arr[i] + '">';
          /*execute a function when someone clicks on the item value (DIV element):*/
          b.addEventListener("click", function(e) {
              /*insert the value for the autocomplete text field:*/
              inp.value = this.getElementsByTagName("input")[0].value;
              /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
              if (inp.value != "OTHERS" && $('#vessel_name_select_id').val() != "OTHERS"){
                  $('#request_form_other_shipping_agent_div').css({"visibility": "hidden", "display":"none"})
                  $('#request_form_other_vessel_name_div').css({"visibility": "hidden", "display":"none"})
              }
              if (inp.value != "OTHERS" && $('#vessel_name_select_id').val() == "OTHERS"){
                  $('#request_form_other_shipping_agent_div').css({"visibility": "hidden", "display":"block"})
                  $('#request_form_other_vessel_name_div').css({"visibility": "visible", "display":"block"})
              }
              closeAllLists();
          });
          a.appendChild(b);
        }
      }
      if (prev_leng < must_show_leng) {
              for (i = prev_leng; i < must_show_leng; i++) {
                  /*create a DIV element for each matching element:*/
                  b = document.createElement("DIV");
                  /*make the matching letters bold:*/
                  // b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                  b.innerHTML += arr[i];
                  /*insert a input field that will hold the current array item's value:*/
                  b.innerHTML += '<input type="hidden" value="' + arr[i] + '">';
                  b.innerHTML = b.innerHTML.replace(val.toUpperCase(), "<strong>"+val.toUpperCase()+"</strong>")
                  /*execute a function when someone clicks on the item value (DIV element):*/
                  b.addEventListener("click", function(e) {
                      /*insert the value for the autocomplete text field:*/
                      inp.value = this.getElementsByTagName("input")[0].value;
                      // hide_show_create_and_edit_shipping_agent();
                      // var shipping_agent = $('#ship_agent_select').val()
                      // create_new_shipping_agent(true, shipping_agent);
                      /*close the list of autocompleted values,
                      (or any other open lists of autocompleted values:*/
                      if (inp.value == "OTHERS" && $('#vessel_name_select_id').val() != "OTHERS"){
                          $('#request_form_other_vessel_name_div').css({"visibility": "hidden", "display":"block"})
                          $('#request_form_other_shipping_agent_div').css({"visibility": "visible", "display":"block"})
                          $("#other_shipping_agent_id").focus()
                      }
                      if (inp.value == "OTHERS" && $('#vessel_name_select_id').val() == "OTHERS"){
                          $('#request_form_other_shipping_agent_div').css({"visibility": "visible", "display":"block"})
                          $("#other_shipping_agent_id").focus()
                      }

                      closeAllLists();
                  });
                  a.appendChild(b);

              }
          }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}
function updateCart (){
     // $(".oe_cart input.js_quantity").trigger("change");
}

function autocomplete_substring(inp, arr) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("input", function(e) {
      var a, b, i, val = this.value;
      /*close any already open lists of autocompleted values*/
      closeAllLists();
      if (!val) { return false;}
      currentFocus = -1;
      /*create a DIV element that will contain the items (values):*/
      a = document.createElement("DIV");
      a.setAttribute("id", this.id + "autocomplete-list");
      a.setAttribute("class", "autocomplete-items");
      /*append the DIV element as a child of the autocomplete container:*/
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      if (val.length >= 3) {
          for (i = 0; i < arr.length; i++) {
            /*check if the item starts with the same letters as the text field value:*/
            if (arr[i].includes(val.toUpperCase())) {
              /*create a DIV element for each matching element:*/
              b = document.createElement("DIV");
              /*make the matching letters bold:*/
              // b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
              b.innerHTML += arr[i];
              /*insert a input field that will hold the current array item's value:*/
              b.innerHTML += '<input type="hidden" value="' + arr[i] + '">';
              b.innerHTML = b.innerHTML.replace(val.toUpperCase(), "<strong>"+val.toUpperCase()+"</strong>")
              /*execute a function when someone clicks on the item value (DIV element):*/
              b.addEventListener("click", function(e) {
                  /*insert the value for the autocomplete text field:*/
                  inp.value = this.getElementsByTagName("input")[0].value;
                  /*close the list of autocompleted values,
                  (or any other open lists of autocompleted values:*/
                  closeAllLists();
              });
              a.appendChild(b);
            }
          }
      }
  });
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
      var x = document.getElementById(this.id + "autocomplete-list");
      if (x) x = x.getElementsByTagName("div");
      if (e.keyCode == 40) {
        /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
        currentFocus++;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 38) { //up
        /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
        currentFocus--;
        /*and and make the current item more visible:*/
        addActive(x);
      } else if (e.keyCode == 13) {
        /*If the ENTER key is pressed, prevent the form from being submitted,*/
        e.preventDefault();
        if (currentFocus > -1) {
          /*and simulate a click on the "active" item:*/
          if (x) x[currentFocus].click();
        }
      }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function (e) {
      closeAllLists(e.target);
  });
}


// function updateCart (){
//      $(".oe_cart input.js_quantity").trigger("change");
// }


(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};

    // todo: auto add to cart not show pop up
    var _t = openerp._t;
    var notification_msg = _t("Success : Product has been added to your shopping cart.");
    // var notification_msg_insufficient = _t("There is insufficient stock to fulfill your request. Please consider the products suggested in");
    // var you_may_also = _t("YOU MAY ALSO BE INTERESTED IN THESE");
    var insufficient_notification_msg = _t("We are sorry, there is insufficient stock to fulfill your request.");
    if (window.location.pathname.includes('/shop/cart') || window.location.pathname.includes('/shop/checkout')) {
        if( $('#process_checkout').length ){
            document.getElementById("process_checkout").addEventListener("mouseover", updateCart)
        }
    }
    $(document).ready(function () {
        var url = window.location.href;
        if (url.search('added=true') > 0) {
            $('.js_sale').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + notification_msg + "</center></strong></div>");
        } else if (url.search('added=false') > 0) {
            if (!document.getElementById('myAlert')) {
                $('.js_sale').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + insufficient_notification_msg + "</div></center></strong></div>");
                $('.featured-products-section').prepend("<div id ='myAlert1' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + insufficient_notification_msg + "</div></center></strong></div>");
                window.scrollTo(0,document.body.scrollHeight);            }
            } else {
                // $('.js_sale').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + notification_msg_insufficient + "<br>" + "<div style='color:#000000'>" + "\"" + you_may_also + "\"" + " (BELOW)" + "</div></center></strong></div>");
            }


        $('#submit_button1').hide();
        // $('#edit_button2').show();
        $('#submit_button2').hide();
        // $('#edit_button3').show();
        $('#submit_button3').hide();
        $('#shipping_agent_name_id').hide();
        $('#shipping_agent_contact_id').hide();
        $('#shipping_agent_cr_number_id').hide();
    });

    if (window.location.pathname.includes('/shop/checkout') || (window.location.pathname.includes('/myaccounts')) || window.location.pathname.includes('/web/signup') || window.location.pathname.includes('/shop/confirm_order')) {
        try {
            if (document.getElementById("insufficient").value == 1) {
                var insufficient_product = document.getElementById("insufficient_product").value
                // var notification_msg_insufficient2 = _t("Sorry, our stock is insufficient to fulfill your request on the following products"
                // + "\n" + insufficient_product);
                $('#cart_instance').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + "Sorry, our stock is insufficient to fulfill your request on the following products:" + "<br/><div style='text-align: left !important;text-indent: 18em !important;'>" + insufficient_product + "</div></center></strong></div>");
            }
        } catch (err) {
            null
        }
        if ($('.oe_cart').length > 0) {
            try {
                document.getElementById("chandler_autocomplete_id1").readOnly = true;
            } catch {

            }
        }
        if ($('.oe_cart').length > 0) {
            try {
                document.getElementById("chandler_autocomplete_id2").readOnly = true;
            } catch {

            }
        }
        if ($('.oe_cart').length > 0) {
            try {
                document.getElementById("chandler_autocomplete_id3").readOnly = true;
            } catch {

            }
        }
        if(document.getElementById("chandler_autocomplete_id1") && !window.location.pathname.includes('/web/signup')){
            document.getElementById("chandler_autocomplete_id1").onclick = function () {
                openerp.jsonRpc('/website_sale/get_chandler_list')
                    .then(function (data) {
                        var chan_dict = JSON.parse(data);
                        var chandlers = chan_dict['chandlers'];
                        //check if chandler2,3 value and remove them from the array
                        var chand2_index = chandlers.indexOf(document.getElementById("chandler_autocomplete_id2").value)
                        if (chand2_index !== -1) {
                            chandlers.splice(chand2_index, 1)
                        }
                        var chand3_index = chandlers.indexOf(document.getElementById("chandler_autocomplete_id3").value)
                        if (chand3_index !== -1) {
                            chandlers.splice(chand3_index, 1)
                        }
                        autocomplete(document.getElementById("chandler_autocomplete_id1"), chandlers);
                    });
            }
        }
         if(document.getElementById("chandler_autocomplete_id2")) {
             document.getElementById("chandler_autocomplete_id2").onclick = function () {
                 openerp.jsonRpc('/website_sale/get_chandler_list')
                     .then(function (data) {
                         var chan_dict = JSON.parse(data);
                         var chandlers = chan_dict['chandlers'];
                         //check if chandler1,3 value and remove them from the array
                         var chand1_index = chandlers.indexOf(document.getElementById("chandler_autocomplete_id1").value)
                         if (chand1_index !== -1) {
                             chandlers.splice(chand1_index, 1)
                         }
                         var chand3_index = chandlers.indexOf(document.getElementById("chandler_autocomplete_id3").value)
                         if (chand3_index !== -1) {
                             chandlers.splice(chand3_index, 1)
                         }
                         autocomplete(document.getElementById("chandler_autocomplete_id2"), chandlers);
                     });
             }
         }
         if(document.getElementById("chandler_autocomplete_id3")) {
            document.getElementById("chandler_autocomplete_id3").onclick = function () {
                openerp.jsonRpc('/website_sale/get_chandler_list')
                    .then(function (data) {
                        var chan_dict = JSON.parse(data);
                        var chandlers = chan_dict['chandlers'];
                        //check if chandler1,2 value and remove them from the array
                        var chand1_index = chandlers.indexOf(document.getElementById("chandler_autocomplete_id1").value)
                        if (chand1_index !== -1) {
                            chandlers.splice(chand1_index, 1)
                        }
                        var chand2_index = chandlers.indexOf(document.getElementById("chandler_autocomplete_id2").value)
                        if (chand2_index !== -1) {
                            chandlers.splice(chand2_index, 1)
                        }
                        autocomplete(document.getElementById("chandler_autocomplete_id3"), chandlers);
                    });
            }}

        }





    var imgIndex = 1;
    try {
        var previous1 = document.getElementById("chandler_id1");
        document.getElementById("chandler1_prev_id").value = previous1.options[previous1.selectedIndex].value;
    } catch(err) {
        null;
    }
    try {
        var previous2 = document.getElementById("chandler_id2");
        document.getElementById("chandler2_prev_id").value = previous2.options[previous2.selectedIndex].value;
    } catch(err) {
        null;
    }
    try {
        var previous3 = document.getElementById("chandler_id3");
        document.getElementById("chandler3_prev_id").value = previous3.options[previous3.selectedIndex].value;
    } catch(err) {
        null;
    }

    if (document.getElementById('chandler_autocomplete_id1')) {
        if (document.getElementById("chandler_autocomplete_id1").value == "") {
            if (window.location.pathname.includes('/shop/checkout')) {
                document.getElementById("chandler_checkbox1").disabled = true;
            }
        }
    }
    if (document.getElementById("chandler_autocomplete_id2")) {
        if (document.getElementById("chandler_autocomplete_id2").value == "") {
            if (window.location.pathname.includes('/shop/checkout')) {
                document.getElementById("chandler_checkbox2").disabled = true;
            }
        }
    }
    if (document.getElementById("chandler_autocomplete_id3")) {
        if (document.getElementById("chandler_autocomplete_id3").value == "") {
            if (window.location.pathname.includes('/shop/checkout')) {
                document.getElementById("chandler_checkbox3").disabled = true;
            }
        }
    }

    if (document.getElementById('vessel_name_select_id')) {
            var vess_nam = document.getElementById('vessel_name_select_id');
            vess_nam.addEventListener('change', hide_show_create_and_edit_vessel_name_signup());
            vess_nam.addEventListener('input', hide_show_create_and_edit_vessel_name_signup());
            vess_nam.addEventListener('click',
                openerp.jsonRpc('/myaccounts/get_vessel_name')
                    .then(function (data) {
                        console.log(data);
                        var data_dict = JSON.parse(data);
                        var vessel_names = data_dict['vessel_name'];
                        var vessel_names = vessel_names.filter(function(e) { return e !== 'OTHERS' })
                            autocomplete_substring_with_length_signup(document.getElementById("vessel_name_select_id"),
                            vessel_names, 2,
                            {'must_show': ['OTHERS']});
                        // hide_show_create_and_edit_vessel_name_signup();
            }));
            $('#vessel_name_select_id').keyup(function () {
                var vess_namtypingTimer2;
                var vess_namtypingTimer2Interval2 = 1000
                clearTimeout(vess_namtypingTimer2);
                // vess_namtypingTimer2 = setTimeout(hide_show_create_and_edit_vessel_name_signup, vess_namtypingTimer2Interval2);
            });
    }
    
    setTimeout(function () {
            if (document.getElementById('vessel_name_select_id')){
                if (document.getElementById('vessel_name_select_id').value == 'OTHERS' && $('#ship_agent_select').val() == "OTHERS"){
                    $('#request_form_other_vessel_name_div').css({"visibility": "visible", "display":"block"})
                    $('#request_form_other_shipping_agent_div').css({"visibility": "visible", "display":"block"})
                }
                if (document.getElementById('vessel_name_select_id').value == 'OTHERS' && $('#ship_agent_select').val() != "OTHERS"){
                    $('#request_form_other_vessel_name_div').css({"visibility": "visible", "display":"block"})
                    $('#request_form_other_shipping_agent_div').css({"visibility": "hidden", "display":"block"})
                }
                }

                if (document.getElementById('ship_agent_select')){
                if (document.getElementById('ship_agent_select').value == 'OTHERS' && $('#vessel_name_select_id').val() == "OTHERS"){
                    $('#request_form_other_vessel_name_div').css({"visibility": "visible", "display":"block"})
                    $('#request_form_other_shipping_agent_div').css({"visibility": "visible", "display":"block"})
                }
                if (document.getElementById('ship_agent_select').value == 'OTHERS' && $('#vessel_name_select_id').val() != "OTHERS"){
                    $('#request_form_other_vessel_name_div').css({"visibility": "hidden", "display":"block"})
                    $('#request_form_other_shipping_agent_div').css({"visibility": "visible", "display":"block"})
                }
            }
    }, 1);





    if (document.getElementById("ship_agent_select")) {
        const ship_agent = document.getElementById('ship_agent_select');
        ship_agent.addEventListener('change', hide_show_create_and_edit_shipping_agent());
        ship_agent.addEventListener('input', hide_show_create_and_edit_shipping_agent());
        ship_agent.addEventListener('click',
            openerp.jsonRpc('/checkout/get_shipping_agent_list')
                .then(function (data) {
                    var data_dict = JSON.parse(data);
                    var shipping_agents = data_dict['shipping_agent'];
                    var shipping_agents = shipping_agents.filter(function(e) { return e !== 'OTHERS' })
                    autocomplete(document.getElementById("ship_agent_select"),
                        shipping_agents,
                        {'must_show': ['OTHERS']});
        }));
        $('#ship_agent_select').keyup(function () {
            var vess_namtypingTimer2;
            var vess_namtypingTimer2Interval2 = 1000
            clearTimeout(vess_namtypingTimer2);
            vess_namtypingTimer2 = setTimeout(hide_show_create_and_edit_shipping_agent, vess_namtypingTimer2Interval2);
        });


        // if (optionExists( 'CREATE..', document.getElementById( 'ship_agent_select' ) ) == false) {
        //     var create_and_edit = document.getElementById("ship_agent_select");
        //     var option = document.createElement("option");
        //     option.text = "CREATE..";
        //     create_and_edit.add(option, document.getElementById("ship_agent_select").length);
        // }
        //
        // $('#ship_agent_select').click(function () {
        //     if (document.getElementById("ship_agent_select").options[document.getElementById("ship_agent_select").selectedIndex].text == "CREATE..") {
        //         $('#shipping_agent_name_id').show();
        //         $('#shipping_agent_contact_id').show();
        //         $('#shipping_agent_cr_number_id').show();
        //         var stars = $('#shipping_agent').find('span')
        //         for (var i=1; i<stars.length;i++){
        //             var input_height = document.getElementById('shipping_agent_name_id').offsetHeight
        //             var distance =  1.8 * input_height + (5 + input_height)* (i-1) + 'px'
        //             stars[i].style.top = distance
        //         }
        //     } else {
        //         $('#shipping_agent_name_id').hide();
        //         $('#shipping_agent_contact_id').hide();
        //         $('#shipping_agent_cr_number_id').hide();
        //         for (var i=1;i<4;i++){
        //             $('#shipping_agent').find('span')[i].style.display='none'
        //         }
        //     }
        // });
    }

    // if (document.getElementById("vessel_name_select_id")) {
    //     if (optionExists( 'CREATE AND EDIT..', document.getElementById( 'vessel_name_select_id' ) ) == false) {
    //         var create_and_edit = document.getElementById("vessel_name_select_id");
    //         var option = document.createElement("option");
    //         option.text = "CREATE AND EDIT..";
    //         create_and_edit.add(option, document.getElementById("vessel_name_select_id").length);
    //     }
    //
    //     $('#vessel_name_select_id').click(function () {
    //         if (document.getElementById("vessel_name_select_id").options[document.getElementById("vessel_name_select_id").selectedIndex].text == "CREATE AND EDIT..") {
    //             $('#vessel_name_id').show();
    //             $('#imo_number_id').show();
    //             $('#vessel_type_select_id').show();
    //             $('#vessel_nrt_id').show();
    //             $('#vessel_flag_id').show();
    //             $('#vessel_crew_id').show();
    //             // $('#shipping_agent_select_id').show();
    //         } else {
    //             $('#vessel_name_id').hide();
    //             $('#imo_number_id').hide();
    //             $('#vessel_type_select_id').hide();
    //             $('#vessel_nrt_id').hide();
    //             $('#vessel_flag_id').hide();
    //             $('#vessel_crew_id').hide();
    //             // $('#shipping_agent_select_id').hide();
    //         }
    //     });
    // }

    // todo: autocomplete on port
    if (document.getElementById("next_port_select_id")) {
        openerp.jsonRpc('/website_sale/get_port_list')
        .then(function (data) {
           var chan_dict = JSON.parse(data);
           var chandlers = chan_dict['port'];
           // autocomplete_substring(document.getElementById("last_port_select_id"), chandlers);
          autocomplete_substring(document.getElementById("next_port_select_id"), chandlers);

        });
    }


    // if (document.getElementById("next_port_select_id")) {
    //     openerp.jsonRpc('/website_sale/get_port_list')
    //     .then(function (data) {
    //        var chan_dict = JSON.parse(data);
    //        var chandlers = chan_dict['port'];
    //     });
    // }


    // end



    if (document.getElementById('edit_button1')) {
        $('#edit_button1').click(function () {
            $('#edit_button1').hide();
            $('#submit_button1').show();
            document.getElementById("chandler_autocomplete_id1").readOnly = false;
        });
    };

    if (document.getElementById('edit_button2')) {
        $('#edit_button2').click(function() {
            $('#edit_button2').hide();
            $('#submit_button2').show();
            document.getElementById("chandler_autocomplete_id2").readOnly = false;
        });
    };

    if (document.getElementById('edit_button3')) {
        $('#edit_button3').click(function () {
            $('#edit_button3').hide();
            $('#submit_button3').show();
            document.getElementById("chandler_autocomplete_id3").readOnly = false;
        });
    };

    if (document.getElementById('submit_button1')) {
        $('#submit_button1').click(function () {
            openerp.jsonRpc('/website_sale/get_chandler_list')
            .then(function (data) {
                var chan_dict = JSON.parse(data);
                var chandlers = chan_dict['chandlers'];
                if (chandlers.includes(document.getElementById("chandler_autocomplete_id1").value) ||
                        document.getElementById("chandler_autocomplete_id1").value === "") {
                    document.getElementById("chandler_autocomplete_id1").readOnly = true;
                    $('#edit_button1').show();
                    $('#submit_button1').hide();
                    if (window.location.pathname.includes('/shop/checkout') & document.getElementById("chandler_autocomplete_id1").value != "") {
                        document.getElementById("chandler_checkbox1").disabled = false;
                    }
                    if (window.location.pathname.includes('/shop/checkout')  & document.getElementById("chandler_autocomplete_id1").value === "") {
                        document.getElementById("chandler_checkbox1").disabled = true;
                    }
                }
                checkout_confirm_button_onmouseover();
            });
        });
    };

    if (document.getElementById('submit_button2')) {
        $('#submit_button2').click(function () {
            openerp.jsonRpc('/website_sale/get_chandler_list')
            .then(function (data) {
                var chan_dict = JSON.parse(data);
                var chandlers = chan_dict['chandlers'];
                if (chandlers.includes(document.getElementById("chandler_autocomplete_id2").value) ||
                        document.getElementById("chandler_autocomplete_id2").value === "") {
                    document.getElementById("chandler_autocomplete_id2").readOnly = true;
                    $('#edit_button2').show();
                    $('#submit_button2').hide();
                    if (window.location.pathname.includes('/shop/checkout')  & document.getElementById("chandler_autocomplete_id2").value != "") {
                        document.getElementById("chandler_checkbox2").disabled = false;
                    }
                    if (window.location.pathname.includes('/shop/checkout')  & document.getElementById("chandler_autocomplete_id2").value === "") {
                        document.getElementById("chandler_checkbox2").disabled = true;
                    }
                }
                checkout_confirm_button_onmouseover();
            });
        });
    };

    if (document.getElementById('submit_button3')) {
        $('#submit_button3').click(function () {
            openerp.jsonRpc('/website_sale/get_chandler_list')
            .then(function (data) {
                var chan_dict = JSON.parse(data);
                var chandlers = chan_dict['chandlers'];
                if (chandlers.includes(document.getElementById("chandler_autocomplete_id3").value) ||
                        document.getElementById("chandler_autocomplete_id3").value === "") {
                    document.getElementById("chandler_autocomplete_id3").readOnly = true;
                    $('#edit_button3').show();
                    $('#submit_button3').hide();
                    if (window.location.pathname.includes('/shop/checkout')) {
                        document.getElementById("chandler_checkbox3").disabled = false;
                    }
                     if (window.location.pathname.includes('/shop/checkout') & document.getElementById("chandler_autocomplete_id3").value === "") {
                        document.getElementById("chandler_checkbox3").disabled = true;
                    }
                }
                checkout_confirm_button_onmouseover();
            });
        });
    };
})();

// $(document).ready(function() {
//     if (window.location.pathname == '/shop/checkout') {
//         window.addEventListener("DOMContentLoaded", theDomHasLoaded, false);
//     }
// })
//
// function theDomHasLoaded(e) {
//      try {
//             //    window.onload = _get_chandler_lists();
//             window.onload = show_hide_buttons();
//             window.onload = read_only_autocomplete_chandler_fields();
//         }
//         catch (err) {
//             null;
//         }
// }

function read_cache_fields() {
    if (document.getElementById('contact_person_cache')) {
        if (document.getElementById('contact_person_cache').value !== "") {
            document.getElementById('contact_person_name').value = document.getElementById('contact_person_cache').value;
        }
    }
    if (document.getElementById('contact_number_cache')) {
        if (document.getElementById('contact_number_cache').value !== "") {
            document.getElementById('contact_person_number').value = document.getElementById('contact_number_cache').value;
        }
    }
    if (document.getElementById('contact_email_cache')) {
        if (document.getElementById('contact_email_cache').value !== "") {
            document.getElementById('contact_person_email').value = document.getElementById('contact_email_cache').value;
        }
    }
    if (document.getElementById('call_sign_cache')) {
        if (document.getElementById('call_sign_cache').value !== "") {
            document.getElementById('callsign').value = document.getElementById('call_sign_cache').value;
        }
    }
    if (document.getElementById('stay_duration_cache')) {
        if (document.getElementById('stay_duration_cache').value !== "") {
            document.getElementById('stay_duration').value = document.getElementById('stay_duration_cache').value;
        }
    }
    if (document.getElementById('estimated_arrival_cache')) {
        if (document.getElementById('estimated_arrival_cache').value !== "") {
            document.getElementById('typedate').value = document.getElementById('estimated_arrival_cache').value;
        }
    }
    if (document.getElementById('imo_cache')) {
        if (document.getElementById('imo_cache').value !== "") {
            document.getElementById('imonumber').value = document.getElementById('imo_cache').value;
        }
    }
    if (document.getElementById('recommend_chandler_name1_cache')) {
        if (document.getElementById('recommend_chandler_name1_cache').value !== "") {
            document.getElementById('recommend_chandler_name1').value = document.getElementById('recommend_chandler_name1_cache').value;
        }
    }
    if (document.getElementById('recommend_chandler_email1_cache')) {
        if (document.getElementById('recommend_chandler_email1_cache').value !== "") {
            document.getElementById('recommend_chandler_email1').value = document.getElementById('recommend_chandler_email1_cache').value;
        }
    }
    if (document.getElementById('recommend_chandler_name2_cache')) {
        if (document.getElementById('recommend_chandler_name2_cache').value !== "") {
            document.getElementById('recommend_chandler_name2').value = document.getElementById('recommend_chandler_name2_cache').value;
        }
    }
    if (document.getElementById('recommend_chandler_email2_cache')) {
        if (document.getElementById('recommend_chandler_email2_cache').value !== "") {
            document.getElementById('recommend_chandler_email2').value = document.getElementById('recommend_chandler_email2_cache').value;
        }
    }
    if (document.getElementById('recommend_chandler_name3_cache')) {
        if (document.getElementById('recommend_chandler_name3_cache').value !== "") {
            document.getElementById('recommend_chandler_name3').value = document.getElementById('recommend_chandler_name3_cache').value;
        }
    }
    if (document.getElementById('recommend_chandler_email3_cache')) {
        if (document.getElementById('recommend_chandler_email3_cache').value !== "") {
            document.getElementById('recommend_chandler_email3').value = document.getElementById('recommend_chandler_email3_cache').value;
        }
    }
    if (document.getElementById('chandler_autocomplete_id1_cache')) {
        if (document.getElementById('chandler_autocomplete_id1_cache').value !== "") {
            document.getElementById('chandler_autocomplete_id1').value = document.getElementById('chandler_autocomplete_id1_cache').value;
        }
    }
    if (document.getElementById('chandler_autocomplete_id2_cache')) {
        if (document.getElementById('chandler_autocomplete_id2_cache').value !== "") {
            document.getElementById('chandler_autocomplete_id2').value = document.getElementById('chandler_autocomplete_id2_cache').value;
        }
    }
    // if (document.getElementById('chandler_autocomplete_id3_cache')) {
    //     if (document.getElementById('chandler_autocomplete_id3_cache').value !== "") {
    //         document.getElementById('chandler_autocomplete_id3').value = document.getElementById('chandler_autocomplete_id3_cache').value;
    //     }
    // }
    if (document.getElementById('chandler_checkbox1_cache')) {
        if (document.getElementById('chandler_checkbox1_cache').value !== "") {
            document.getElementById('chandler_checkbox1').value = document.getElementById('chandler_checkbox1_cache').value;
        }
    }
    if (document.getElementById('chandler_checkbox2_cache')) {
        if (document.getElementById('chandler_checkbox2_cache').value !== "") {
            document.getElementById('chandler_checkbox2').value = document.getElementById('chandler_checkbox2_cache').value;
        }
    }
    if (document.getElementById('chandler_checkbox3_cache')) {
        if (document.getElementById('chandler_checkbox3_cache').value !== "") {
            document.getElementById('chandler_checkbox3').value = document.getElementById('chandler_checkbox3_cache').value;
        }
    }
    if (document.getElementById('next_port_cache')) {
        if (document.getElementById('next_port_cache').value !== "") {
            document.getElementById('next_port_select_id').value = document.getElementById('next_port_cache').value;
        }
    }
    if (document.getElementById('last_port_cache')) {
        if (document.getElementById('last_port_cache').value !== "") {
            document.getElementById('last_port_select_id').value = document.getElementById('last_port_cache').value;
        }
    }
    if (document.getElementById('vessel_name_dropdown_cache')) {
        if (document.getElementById('vessel_name_dropdown_cache').value !== "") {
            document.getElementById('vessel_name_select_id').value = document.getElementById('vessel_name_dropdown_cache').value;
            if (document.getElementById('vessel_name_select_id').value === "CREATE AND EDIT..") {
                if (document.getElementById('vessel_name_cache').value !== "") {
                    document.getElementById('vessel_name_id').value = document.getElementById('vessel_name_cache').value;
                }
                if (document.getElementById('vessel_imo_number_cache').value !== "") {
                    document.getElementById('imo_number_id').value = document.getElementById('vessel_imo_number_cache').value;
                }
                if (document.getElementById('vessel_nrt_cache').value !== "") {
                    document.getElementById('vessel_nrt_id').value = document.getElementById('vessel_nrt_cache').value;
                }
                if (document.getElementById('vessel_flag_cache').value !== "") {
                    document.getElementById('vessel_flag_id').value = document.getElementById('vessel_flag_cache').value;
                }
                if (document.getElementById('vessel_crew_num_cache').value !== "") {
                    document.getElementById('vessel_crew_id').value = document.getElementById('vessel_crew_num_cache').value;
                }
                if (document.getElementById('vessel_name_type_cache').value !== "") {
                    document.getElementById('vessel_type_select_id').value = document.getElementById('vessel_name_type_cache').value;
                }
            }
        }
    }
    if (document.getElementById('shipping_agent_dropdown_cache')) {
        if (document.getElementById('shipping_agent_dropdown_cache').value !== "") {
            document.getElementById('ship_agent_select').value = document.getElementById('shipping_agent_dropdown_cache').value;
            if (document.getElementById('ship_agent_select').value === "CREATE AND EDIT..") {
                if (document.getElementById('shipping_agent_name_cache').value !== "") {
                    document.getElementById('shipping_agent_name_id').value = document.getElementById('shipping_agent_name_cache').value;
                }
                if (document.getElementById('shipping_agent_contact_cache').value !== "") {
                    document.getElementById('shipping_agent_contact_id').value = document.getElementById('shipping_agent_contact_cache').value;
                }
                if (document.getElementById('shipping_agent_cr_num_cache').value !== "") {
                    document.getElementById('shipping_agent_cr_number_id').value = document.getElementById('shipping_agent_cr_num_cache').value;
                }
            }
        }
    }
    if (document.getElementById('vessel_type_cache')) {
        if (document.getElementById('vessel_type_cache').value !== "") {
            document.getElementById('vessel_type_dropdown_select_id').value = document.getElementById('vessel_type_cache').value;
        }
    }
}

try {
//    window.onload = _get_chandler_lists();
    window.onload = show_hide_buttons();
    if (document.getElementById('chandler_checkbox1') && document.getElementById('chandler_autocomplete_id1')) {
        if (document.getElementById('chandler_autocomplete_id1').value !== "") {
            document.getElementById('chandler_checkbox1').checked = true;
        }
    }
    if (document.getElementById('chandler_checkbox2') && document.getElementById('chandler_autocomplete_id2')) {
        if (document.getElementById('chandler_autocomplete_id2').value !== "") {
            document.getElementById('chandler_checkbox2').checked = true;
        }
    }
    if (document.getElementById('chandler_checkbox3') && document.getElementById('chandler_autocomplete_id3')) {
        if (document.getElementById('chandler_autocomplete_id3').value !== "") {
            document.getElementById('chandler_checkbox3').checked = true;
        }
    }

    window.onload = read_cache_fields();
    // window.onload = read_only_autocomplete_chandler_fields();
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};
    website.ready().done(function () {
        if (document.getElementById("vessel_name_dropdown_cache")) {
            if (document.getElementById("vessel_name_dropdown_cache").value === "CREATE AND EDIT..") {
                $('#vessel_name_id').show();
                $('#imo_number_id').show();
                $('#vessel_type_select_id').show();
                $('#vessel_nrt_id').show();
                $('#vessel_flag_id').show();
                $('#vessel_crew_id').show();
            } else {
                $('#vessel_name_id').hide();
                $('#imo_number_id').hide();
                $('#vessel_type_select_id').hide();
                $('#vessel_nrt_id').hide();
                $('#vessel_flag_id').hide();
                $('#vessel_crew_id').hide();
            }
        }
        if (document.getElementById("shipping_agent_dropdown_cache")) {
            if (document.getElementById("shipping_agent_dropdown_cache").value === "CREATE AND EDIT..") {
                $('#shipping_agent_name_id').show();
                $('#shipping_agent_contact_id').show();
                $('#shipping_agent_cr_number_id').show();
            } else {
                $('#shipping_agent_name_id').hide();
                $('#shipping_agent_contact_id').hide();
                $('#shipping_agent_cr_number_id').hide();
            }
        }
        var msg = '';
        if (document.getElementsByClassName('has-error').length > 0) {
            if (document.getElementById("fill_mandatory_fields")) {
                msg = '<p>Please fill up the mandatory fields in asterisk (*)</p>\n';
                //   man + port
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n' + '<p>Please input the correct Next Port of Call</p>';
                }
                // man + port + shipping
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!=''){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Next Port of Call</p>\n'
                         + '<p>Please input the correct Shipping Agent</p>';
                }
                // man + port + shipping + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='') {
                    msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                        + '<p>Please input the correct Next Port of Call</p>\n'
                        + '<p>Please input the correct Shipping Agent</p>'
                        + '<p>Please input the correct Vessel Name</p>';
                }
                var delayInMilliseconds = 100; //1 second
                setTimeout(function() {
                    //your code to be executed after 1 second
                    document.getElementById("fill_mandatory_fields").innerHTML = "";

                    $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                }, delayInMilliseconds);
            }
            if (document.getElementById("error_msg_prompt")) {
                var delayInMilliseconds = 100; //1 second
                msg = '<p>Please fill up the mandatory fields in asterisk (*)</p>\n';
                //   man + port
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1){
                    msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n' + '<p>Please input the correct Next Port of Call</p>';
                }
                // man + shipping
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') == -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    document.getElementsByClassName('has-error').length > 1){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Shipping Agent</p>'
                }
                // man + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') == -1 &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length > 1){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Vessel Name</p>'
                }
                // shipping + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') == -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length == 2){
                     msg = '<p>Please input the correct Shipping Agent</p>\n'
                         + '<p>Please input the correct Vessel Name</p>';
                }
                // man + shipping + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') == -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length > 2){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Shipping Agent</p>\n'
                         + '<p>Please input the correct Vessel Name</p>';
                }
                // port + shipping
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    document.getElementsByClassName('has-error').length == 2){
                    msg  = '<p>Please input the correct Shipping Agent</p>\n'
                         + '<p>Please input the correct Next Port of Call</p>';
                }
                // man + port + shipping
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    document.getElementsByClassName('has-error').length > 2){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Shipping Agent</p>\n'
                         + '<p>Please input the correct Next Port of Call</p>';
                }
                // port + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length == 2){
                    msg  = '<p>Please input the correct Vessel Name</p>\n'
                         + '<p>Please input the correct Next Port of Call</p>';
                }
                // man + port + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length > 2){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Vessel Name</p>\n'
                         + '<p>Please input the correct Next Port of Call</p>';
                }
                // port + shipping + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length == 3){

                    msg  = '<p>Please input the correct Shipping Agent</p>\n'
                         + '<p>Please input the correct Vessel Name</p>\n'
                         + '<p>Please input the correct Next Port of Call</p>';
                }
                // man + port + shipping + vessel
                if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#ship_agent_select').val()!='' &&
                    $('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 &&
                    $('#vessel_name_select_id').val()!='' &&
                    document.getElementsByClassName('has-error').length > 3){
                     msg = '<p>Please fill up the mandatory fields in asterisk (*) </p>\n'
                         + '<p>Please input the correct Shipping Agent</p>\n'
                         + '<p>Please input the correct Vessel Name</p>\n'
                         + '<p>Please input the correct Next Port of Call</p>';
                }
                setTimeout(function() {
                //your code to be executed after 1 second
                    document.getElementById("error_msg_prompt").innerHTML = "";
                    $('#error_msg_prompt').append("<div id ='myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                }, delayInMilliseconds);
            }
            check_estimated_arrival_before_date_order();
        }
        if (document.getElementById('next_port_select_id')){
            if ($('#next_port_select_id').offsetParent().attr('class').indexOf('has-error') > -1 && document.getElementsByClassName('has-error').length ==1){
                if (document.getElementById("fill_mandatory_fields")) {
                    msg = '<p>Please input the correct Next Port of Call</p>';
                    var delayInMilliseconds = 100; //1 second
                    setTimeout(function () {
                        //your code to be executed after 1 second
                        document.getElementById("fill_mandatory_fields").innerHTML = "";

                        $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
                if (document.getElementById("error_msg_prompt")) {
                    var delayInMilliseconds = 100; //1 second
                    msg = '<p>Please input the correct Next Port of Call</p>';
                    setTimeout(function() {
                    //your code to be executed after 1 second
                        document.getElementById("error_msg_prompt").innerHTML = "";
                        $('#error_msg_prompt').append("<div id ='myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
            }
        }

        if (document.getElementById('ship_agent_select')){
            if ($('#ship_agent_select').offsetParent().attr('class').indexOf('has-error') > -1 && document.getElementsByClassName('has-error').length ==1 && $('#ship_agent_select').val()!=''){
                if (document.getElementById("fill_mandatory_fields")) {
                    msg = '<p>Please input the correct Shipping Agent</p>';
                    var delayInMilliseconds = 100; //1 second
                    setTimeout(function () {
                        //your code to be executed after 1 second
                        document.getElementById("fill_mandatory_fields").innerHTML = "";
                        $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
                if (document.getElementById("error_msg_prompt")) {
                    var delayInMilliseconds = 100; //1 second
                    msg = '<p>Please input the correct Shipping Agent</p>';
                    setTimeout(function() {
                    //your code to be executed after 1 second
                        document.getElementById("error_msg_prompt").innerHTML = "";
                        $('#error_msg_prompt').append("<div id ='myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
            }
        }

        if (document.getElementById('vessel_name_select_id')){
            if ($('#vessel_name_select_id').offsetParent().attr('class').indexOf('has-error') > -1 && document.getElementsByClassName('has-error').length ==1 && $('#vessel_name_select_id').val()!=''){
                if (document.getElementById("fill_mandatory_fields")) {
                    msg = '<p>Please input the correct Vessel Name</p>';
                    var delayInMilliseconds = 100; //1 second
                    setTimeout(function () {
                        //your code to be executed after 1 second
                        document.getElementById("fill_mandatory_fields").innerHTML = "";
                        $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
                if (document.getElementById("error_msg_prompt")) {
                    var delayInMilliseconds = 100; //1 second
                    msg = '<p>Please input the correct Vessel Name</p>';
                    setTimeout(function() {
                    //your code to be executed after 1 second
                        document.getElementById("error_msg_prompt").innerHTML = "";
                        $('#error_msg_prompt').append("<div id ='myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
            }
        }

    });
} catch (err) {
    console.log(err);
}


function checkout_confirm_button_onmouseover() {
    var msg = "";
    var sb1msg = "";
    var sb2msg = "";
    var sb3msg = "";
    var sb1msg_flag = false;
    var sb2msg_flag = false;
    var sb3msg_flag = false;
    var chan_dict = [];
    var chandlers = [];
    var chandlers_email = [];
    var checkbox_flag = false;
    openerp.jsonRpc('/website_sale/get_chandler_list')
    .then(function (data) {
        chan_dict = JSON.parse(data);
        chandlers_email = chan_dict['chandlers_email'];
        chandlers = chan_dict['chandlers'];
        // check if any preferred chandler is ticked
        if (document.getElementById('chandler_checkbox1').checked === false &&
            document.getElementById('chandler_checkbox2').checked === false &&
            document.getElementById('chandler_checkbox3').checked === false) {
            checkbox_flag = true;
            // msg = msg + "Please tick at least one chandler before proceeding!\n\n"
            msg = msg + "Please select one chandler before proceeding!\n\n"
        }

        if (document.getElementById("submit_button1")) {
            if ($('#submit_button1').is(":visible")) {
                $('#chandler_autocomplete_id1').removeClass('form-control').addClass('form-control-red-border');
                // $('#checkout_confirm_button').hide();
                // alert(msg);
                if (chandlers.includes(document.getElementById("chandler_autocomplete_id1").value) ||
                    document.getElementById("chandler_autocomplete_id1").value === "") {
                    // no need throw alert
                } else {
                    sb1msg = document.getElementById("chandler_autocomplete_id1").value;
                    sb1msg_flag = true;
                }
            } else {
                $('#chandler_autocomplete_id1').removeClass('form-control-red-border').addClass('form-control');
            }
        }

        if (document.getElementById("submit_button2")) {
            if ($('#submit_button2').is(":visible")) {
                $('#chandler_autocomplete_id2').removeClass('form-control').addClass('form-control-red-border');
                // $('#checkout_confirm_button').hide();
                // alert(msg);
                if (chandlers.includes(document.getElementById("chandler_autocomplete_id2").value) ||
                    document.getElementById("chandler_autocomplete_id2").value === "") {
                    // no need throw alert
                } else {
                    sb2msg = document.getElementById("chandler_autocomplete_id2").value;
                    sb2msg_flag = true;
                }
            } else {
                $('#chandler_autocomplete_id2').removeClass('form-control-red-border').addClass('form-control');
            }
        }

        if (document.getElementById("submit_button3")) {
            if ($('#submit_button3').is(":visible")) {
                $('#chandler_autocomplete_id3').removeClass('form-control').addClass('form-control-red-border');
                // $('#checkout_confirm_button').hide();
                // alert(msg);
                if (chandlers.includes(document.getElementById("chandler_autocomplete_id3").value) ||
                    document.getElementById("chandler_autocomplete_id3").value === "") {
                    // no need throw alert
                } else {
                    sb3msg = document.getElementById("chandler_autocomplete_id3").value;
                    sb3msg_flag = true;
                }
            } else {
                $('#chandler_autocomplete_id3').removeClass('form-control-red-border').addClass('form-control');
            }
        }

        if (sb1msg_flag || sb2msg_flag || sb3msg_flag) {
            msg = msg + "You need to click submit on chandler before you can confirm this request!\n\n";
            if (sb1msg_flag) {
                msg = msg + sb1msg + " does not exist in our system.\n"
            }
            if (sb2msg_flag) {
                msg = msg + sb2msg + " does not exist in our system.\n"
            }
            if (sb3msg_flag) {
                msg = msg + sb3msg + " does not exist in our system.\n"
            }
            // alert(msg);
        }
        // if (document.getElementById("submit_button1") && document.getElementById("submit_button2") && document.getElementById("submit_button3")) {
        //     if ($('#submit_button3').is(":hidden") && $('#submit_button2').is(":hidden") && $('#submit_button1').is(":hidden")) {
        //         $('#checkout_confirm_button').show();
        //     }
        // }

        //   ____ _               _                     _     _                    _
        //  / ___| |__   ___  ___| | __  _ __ ___  __ _(_)___| |_ ___ _ __ ___  __| |
        // | |   | '_ \ / _ \/ __| |/ / | '__/ _ \/ _` | / __| __/ _ \ '__/ _ \/ _` |
        // | |___| | | |  __/ (__|   <  | | |  __/ (_| | \__ \ ||  __/ | |  __/ (_| |
        //  \____|_| |_|\___|\___|_|\_\ |_|  \___|\__, |_|___/\__\___|_|  \___|\__,_|
        //                                        |___/
        //       _                     _ _
        //   ___| |__   __ _ _ __   __| | | ___ _ __
        //  / __| '_ \ / _` | '_ \ / _` | |/ _ \ '__|
        // | (__| | | | (_| | | | | (_| | |  __/ |
        //  \___|_| |_|\__,_|_| |_|\__,_|_|\___|_|
        var rcname1_flag = false;
        var rcemail1_flag = false;
        var rcname2_flag = false;
        var rcemail2_flag = false;
        var rcname3_flag = false;
        var rcemail3_flag = false;
        if (document.getElementById("recommend_chandler_name1") &&
            document.getElementById("recommend_chandler_email1") &&
            document.getElementById("recommend_chandler_name2") &&
            document.getElementById("recommend_chandler_email2") &&
            document.getElementById("recommend_chandler_name3") &&
            document.getElementById("recommend_chandler_email3")) {
            var rcname1_flag = false;
            var rcemail1_flag = false;
            var rcname2_flag = false;
            var rcemail2_flag = false;
            var rcname3_flag = false;
            var rcemail3_flag = false;
            var rcname1_msg = "";
            var rcemail1_msg = "";
            var rcname2_msg = "";
            var rcemail2_msg = "";
            var rcname3_msg = "";
            var rcemail3_msg = "";
            if (document.getElementById("recommend_chandler_name1").value !== "" ||
                document.getElementById("recommend_chandler_email1").value !== "") {

                if (!chandlers.includes(document.getElementById("recommend_chandler_name1").value.trim()) ||
                    document.getElementById("recommend_chandler_name1").value === "" ||
                    chandlers.length === 0) {
                    // nothing to do here
                } else {
                    rcname1_flag = true;
                    rcname1_msg = document.getElementById("recommend_chandler_name1").value.trim() + " has already registered with us.\n";
                }
                if (!chandlers_email.includes(document.getElementById("recommend_chandler_email1").value.trim()) ||
                    document.getElementById("recommend_chandler_email1").value === "" ||
                    chandlers_email.length === 0) {
                    // nothing to do here
                } else {
                    rcemail1_flag = true;
                    rcemail1_msg = document.getElementById("recommend_chandler_email1").value.trim() + " has already registered with us.\n";
                }
            }

            if (document.getElementById("recommend_chandler_name2").value !== "" ||
                document.getElementById("recommend_chandler_email2").value !== "") {

                if (!chandlers.includes(document.getElementById("recommend_chandler_name2").value.trim()) ||
                    document.getElementById("recommend_chandler_name2").value === "" ||
                    chandlers.length === 0) {
                    // nothing to do here
                } else {
                    rcname2_flag = true;
                    rcname2_msg = document.getElementById("recommend_chandler_name2").value.trim() + " has already registered with us.\n";
                }
                if (!chandlers_email.includes(document.getElementById("recommend_chandler_email2").value.trim()) ||
                    document.getElementById("recommend_chandler_email2").value === "" ||
                    chandlers_email.length === 0) {
                    // nothing to do here
                } else {
                    rcemail2_flag = true;
                    rcemail2_msg = document.getElementById("recommend_chandler_email2").value.trim() + " has already registered with us.\n";
                }
            }

            if (document.getElementById("recommend_chandler_name3").value !== "" ||
                document.getElementById("recommend_chandler_email3").value !== "") {

                if (!chandlers.includes(document.getElementById("recommend_chandler_name3").value.trim()) ||
                    document.getElementById("recommend_chandler_name3").value === "" ||
                    chandlers.length === 0) {
                    // nothing to do here
                } else {
                    rcname3_flag = true;
                    rcname3_msg = document.getElementById("recommend_chandler_name3").value.trim() + " has already registered with us.\n";
                }
                if (!chandlers_email.includes(document.getElementById("recommend_chandler_email3").value.trim()) ||
                    document.getElementById("recommend_chandler_email3").value === "" ||
                    chandlers_email.length === 0) {
                    // nothing to do here
                } else {
                    rcemail3_flag = true;
                    rcemail3_msg = document.getElementById("recommend_chandler_email3").value.trim() + " has already registered with us.\n";
                }
            }

        }
        if (rcname1_flag || rcname2_flag || rcname3_flag || rcemail1_flag || rcemail2_flag || rcemail3_flag) {
            if (msg.length > 0) {
                msg = msg + "\nAND/OR\n\n";
            }
            if (rcname1_flag || rcemail1_flag) {
                if (rcname1_flag) {
                    msg = msg + rcname1_msg;
                }
                if (rcemail1_flag) {
                    msg = msg + rcemail1_msg;
                }
            }

            if (rcname2_flag || rcemail2_flag) {
                if (rcname2_flag) {
                    msg = msg + rcname2_msg;
                }
                if (rcemail2_flag) {
                    msg = msg + rcemail2_msg;
                }
            }

            if (rcname3_flag || rcemail3_flag) {
                if (rcname3_flag) {
                    msg = msg + rcname3_msg;
                }
                if (rcemail3_flag) {
                    msg = msg + rcemail3_msg;
                }
            }

            if (msg.length > 0) {
                msg = msg + "Please recommend other chandlers.\n";
            }
        }
        if ((sb1msg_flag || sb2msg_flag || sb3msg_flag || rcname1_flag || rcname2_flag || rcname3_flag || rcemail1_flag || rcemail2_flag || rcemail3_flag || checkbox_flag) && msg.length > 0) {
            if (document.getElementById("fill_mandatory_fields")) {
                if (document.getElementById('myAlert1')) {
                    document.getElementById('myAlert1').remove();
                }
                $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
            }
            if (document.getElementById("error_msg_prompt")) {
                if (document.getElementById('myAlert2')) {
                    document.getElementById('myAlert2').remove();
                }
                $('#error_msg_prompt').append("<div id ='myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
            }
            // alert(msg);
        }
        // check_estimated_arrival_before_date_order();
    });
}
var notification = 0;

function checkout_confirm_button_onclick() {
    // if ($('#submit_button1').is(":visible") && $('#submit_button2').is(":visible") && $('#submit_button3').is(":visible")) {
    //     alert('You need to click submit on each chandler before you can confirm this request!');
    //
    // }
    if (((document.getElementById("recommend_chandler_name1").value != "") ||
        (document.getElementById("recommend_chandler_name2").value != "") ||
        (document.getElementById("recommend_chandler_name3").value != "")) &&
        (notification == 0)){
        var haveChan1 = false;
        var haveChan2 = false;
        var haveChan3 = false;
        var msg = '';
        var msg1 = 'The Chandler(s) ';
        var comma = ' ';
        var chan_name1 = document.getElementById('recommend_chandler_name1');
        var chan_name2 = document.getElementById('recommend_chandler_name2');
        var chan_name3 = document.getElementById('recommend_chandler_name3');
        var msg2 = "is not registered in the system. We will still submit your request to the Chandler(s).\n" +
            '\n' +
            "Kindly note that processing of your enquiry is subjected to Chandler(s)' registration with the system.";
        if (chan_name1.value) {
            msg = msg1 + chan_name1.value;
            haveChan1 = true;
        }
        if (chan_name2.value) {
            if (haveChan1) {
              msg = msg + comma
            }
            msg = msg + chan_name2.value;
            haveChan2 = true;
        }
        if (chan_name3.value) {
            if (haveChan2) {
              msg = msg + comma
            }
            msg = msg + chan_name3.value;
            haveChan3 = true;
        }
        if (haveChan1 || haveChan2 || haveChan3) {
              msg = msg + comma
        }

        msg = msg + msg2;

        alert(msg);
        notification = notification + 1;
    }

    if (document.getElementById("chandler_autocomplete_id1") &&
                document.getElementById("chandler_autocomplete_id2") &&
                document.getElementById("chandler_autocomplete_id3")) {
                var pc_one = document.getElementById("chandler_autocomplete_id1").value;
                var pc_two = document.getElementById("chandler_autocomplete_id2").value;
                var pc_three = document.getElementById("chandler_autocomplete_id3").value;
                var matches = [];
                openerp.jsonRpc('/_website_myaccount/_get_approved_chandler_list')
                    .then(function (o) {
                        var data = JSON.parse(o);
                        // check if entered chandler is in approved list
                        // names in matches list are names found in database
                        for (var idx = 0; idx < data.approved_chandlers.length; idx++) {
                            if (data.approved_chandlers[idx] === pc_one) {
                                matches.push(data.approved_chandlers[idx]);
                            } else if (data.approved_chandlers[idx] === pc_two) {
                                matches.push(data.approved_chandlers[idx]);
                            } else if (data.approved_chandlers[idx] === pc_three) {
                                matches.push(data.approved_chandlers[idx]);
                            }
                        }

                        // concaternate chandler names if they are not found in the database
                        var conditional_flag1 = false;
                        var conditional_flag2 = false;
                        var conditional_flag3 = false;
                        var msg = "Chandler(s) ";
                        if (pc_one !== "" && !(matches.includes(pc_one))) {
                            msg = msg + pc_one + ' ';
                            conditional_flag1 = true;
                        } else if (pc_two !== "" && !(matches.includes(pc_two))) {
                            msg = msg + pc_two + ' ';
                            conditional_flag2 = true;
                        } else if (pc_three !== "" && !(matches.includes(pc_three))) {
                            msg = msg + pc_three + ' ';
                            conditional_flag3 = true;
                        }

                        // select chandlers found in database to be updated
                        if (conditional_flag1 === true || conditional_flag2 === true || conditional_flag3 === true) {
                            msg = msg + 'does not exist in the database, the chandler(s) will not be saved.';
                        }
                        var vname = document.getElementsByName("vessel_name")[0]
                        var vtype = document.getElementsByName("vessel_type")[0]
                        var param = {
                                'email': document.getElementsByName("email")[0].value,
                                'vname': vname.options[vname.selectedIndex].text,
                                'vtype': vtype.options[vname.selectedIndex].text,
                                'name': document.getElementsByName("name")[0].value,
                                'imo': document.getElementsByName("imo_number")[0].value,
                                'call_sign': document.getElementsByName("call_sign")[0].value,
                                'tel': document.getElementsByName("phone")[0].value,
                                context: _.extend(openerp.website.get_context()),
                        };
                        if (conditional_flag1 === false && pc_one !== "" && matches.includes(pc_one)) {param['pc_one']=pc_one}
                        if (conditional_flag2 === false && pc_two !== "" && matches.includes(pc_two)) {param['pc_two']=pc_two}
                        if (conditional_flag3 === false && pc_three !== "" && matches.includes(pc_three)) {param['pc_three']=pc_three}
                        openerp.jsonRpc('/_website_myaccount/_update_account_info', 'call', {value:param})
                    })
    }
    check_estimated_arrival_before_date_order();
}

if (document.getElementById('checkout_confirm_button')) {
    const checkout_confirm_button = document.getElementById('checkout_confirm_button');
    checkout_confirm_button.addEventListener('mouseover', checkout_confirm_button_onmouseover);
    checkout_confirm_button.addEventListener('click', checkout_confirm_button_onclick);
}

if (document.getElementById('date_order')) {
    const est_arrival = document.getElementById('typedate');
    est_arrival.onchange = check_estimated_arrival_before_date_order;
}

function check_estimated_arrival_before_date_order(ev) {
    // null
    if ((document.getElementById('typedate').value !== "") &&
        (document.getElementById('date_order').value !== "")) {
        var order_split = document.getElementById('date_order').value.split('/');
        var type_split = document.getElementById('typedate').value.split('/');
        var type_string = type_split[2]+'-'+ type_split[1] +'-'+ type_split[0];
        var type_date = Date.parse(type_string);
        var order_string = order_split[2]+'-'+ order_split[1] +'-'+ order_split[0];
        var order_date = Date.parse(order_string);
        var display_date = order_split[0]+'/'+ order_split[1] +'/'+ order_split[2];
        var msg = 'Estimated Date of Arrival cannot be earlier than ' + display_date;
        var msg_empty = 'Estimated Date of Arrival cannot be empty!';

        if (order_date > type_date) {
            if (document.getElementById("fill_mandatory_fields")) {
                if (document.getElementById('myAlert1')) {
                    if (document.getElementById('myAlert1').innerHTML.includes('Estimated Date of Arrival cannot be earlier than ')) {
                        var phrase_index1 = document.getElementById('myAlert1').innerHTML.indexOf('Estimated Date of Arrival cannot be earlier than ');
                        var phrase_length1 = 'Estimated Date of Arrival cannot be earlier than '.length;
                        var start_index1 = phrase_index1 + phrase_length1;
                        var end_index1 = start_index1 + 10;   // YYYY-MM-DD is 10 characters including dash
                        document.getElementById('myAlert1').innerHTML = document.getElementById('myAlert1').innerHTML.replace(document.getElementById('myAlert1').innerHTML.substring(start_index1,end_index1),display_date);
                    }  else {
                        document.getElementById('myAlert1').innerHTML = document.getElementById('myAlert1').innerHTML + "<strong><center>" + msg + "</center></strong>"
                    }
                } else {
                    $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                }
            }
            if (document.getElementById("error_msg_prompt")) {
                if (document.getElementById('myAlert2')) {
                    if (document.getElementById('myAlert2').innerHTML.includes('Estimated Date of Arrival cannot be earlier than ')) {
                        var phrase_index2 = document.getElementById('myAlert2').innerHTML.indexOf('Estimated Date of Arrival cannot be earlier than ');
                        var phrase_length2 = 'Estimated Date of Arrival cannot be earlier than '.length;
                        var start_index2 = phrase_index2 + phrase_length2;
                        var end_index2 = start_index2 + 10;   // YYYY-MM-DD is 10 characters including dash
                        document.getElementById('myAlert2').innerHTML = document.getElementById('myAlert2').innerHTML.replace(document.getElementById('myAlert2').innerHTML.substring(start_index2,end_index2),display_date);
                    }  else {
                        document.getElementById('myAlert2').innerHTML = document.getElementById('myAlert2').innerHTML + "<strong><center>" + msg + "</center></strong>"
                    }
                } else {
                    $('#error_msg_prompt').append("<div id ='myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                }
            }
        } else {
            if (document.getElementById("fill_mandatory_fields")) {
                if (document.getElementById('myAlert1')) {
                    document.getElementById('myAlert1').remove();
                }
            }
            if (document.getElementById("error_msg_prompt")) {
                if (document.getElementById('myAlert2')) {
                    document.getElementById('myAlert2').remove();
                }
            }
        }
    }
}