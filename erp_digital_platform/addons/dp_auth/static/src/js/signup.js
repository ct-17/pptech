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


function autocomplete_substring_with_length_signup(inp, arr, leng, context={}) {
    /*
    context = {'must_show': array}
     */

  filler = document.createElement("DIV");
  // filler.setAttribute("class", "row-space-filler")
  document.getElementById('autocompletevesselnamehere').appendChild(filler);
  prev_leng = arr.length;
  must_show_leng = 0;
  if ('must_show' in context) {
      arr = arr.concat(context['must_show']);
      must_show_leng = arr.length;
  }
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
      document.getElementById('autocompletevesselnamehere').appendChild(a);
      /*for each item in the array...*/
      if (val.length >= leng) {
          for (i = 0; i < prev_leng; i++) {
            /*check if the item starts with the same letters as the text field value:*/
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
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
                  openerp.jsonRpc('/get_chandler_data', 'call', {
                            'vessel_name':  this.getElementsByTagName("input")[0].value,})
                    .then(function (data) {
                        var chan_dict = JSON.parse(data);
                        $("#imo").val(chan_dict['imo_number'])
                        $("#signup_vessel_type").val(chan_dict['vessel_type'].toString());
                        $("#vessel_type_dropdown_select_id").val(chan_dict['vessel_type_name'].toString());
                     });
                  if (inp.value != "OTHERS" && $('#ship_agent_select').val() != "OTHERS"){
                      $('#request_form_other_shipping_agent_div').css({"visibility": "hidden", "display":"none"})
                      $('#request_form_other_vessel_name_div').css({"visibility": "hidden", "display":"none"})
                      $('#vessel_type_dropdown_select_id').val('')
                  }
                  if (inp.value != "OTHERS" && $('#ship_agent_select').val() == "OTHERS"){
                      $('#request_form_other_shipping_agent_div').css({"visibility": "visible", "display":"block"})
                      $('#request_form_other_vessel_name_div').css({"visibility": "hidden", "display":"block"})
                      $('#vessel_type_dropdown_select_id').val('')
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
                      if (inp.value == "OTHERS" && $('#ship_agent_select').val() != "OTHERS"){
                          $('#request_form_other_shipping_agent_div').css({"visibility": "hidden", "display":"block"})
                          $('#request_form_other_vessel_name_div').css({"visibility": "visible", "display":"block"})
                          $("#other_vessel_name_id").focus();
                      }
                      if (inp.value == "OTHERS" && $('#ship_agent_select').val() == "OTHERS"){
                          $('#request_form_other_vessel_name_div').css({"visibility": "visible", "display":"block"})
                          $("#other_vessel_name_id").focus();
                      }
                      // hide_show_create_and_edit_vessel_name_signup();
                      var vessel_name = $('#vessel_name_select_id').val()
                      // create_new_vessel(true, vessel_name);
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


function create_new_vessel(flag, create_vessel_name) {
    if (flag && !document.getElementById('modal_create_new_vessel')) {
        var website = openerp.website;
        website.openerp_website = {};
        var $form = $('.oe_website_login_container');
        openerp.jsonRpc('/create_new_vessel_name', 'call', {
               context: _.extend({'open_vessel_form': 'True', 'vessel_type': $("#signup_vessel_type").val(), 'vessel_name': create_vessel_name}, openerp.website.get_context())
            }).then(function (modal) {
            self = this;

            var $modal = $(modal);
            if (!document.getElementById('modal_create_new_vessel')) {
                $modal.appendTo($form)
                .modal()
                .on('hidden.bs.modal', function () {
                    $(this).remove();
                });

                $('.oe_website_login_container').fadeIn();
                $modal.fadeOut();

                $('#new_shipmaster_create_vessel').click(function(ev) {
                    if ($("#vessel_name_id").val() === "" || $("#vessel_flag_id").val() === "" || $("#vessel_type_select_id").val() === "") {
                        var msg = "Please fill up the mandatory fields in asterisk (*)";
                        var required_fields = document.getElementById('modal_create_new_vessel').querySelectorAll('[required="required"]'),i;
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
                            if (!document.getElementById('create_vessel_name_myAlert1')){
                                var msg = '<p>Please fill up the mandatory fields in asterisk (*)</p>\n';
                                var delayInMilliseconds = 100;
                                setTimeout(function() {
                                    $('#fill_mandatory_fields').append("<div id ='create_vessel_name_myAlert1' class ='alert alert-danger'><div id='novesselname'><strong><center>" + msg + "</center></strong></div></div>");
                                    $('#new_shipmaster_create_vessel').parent().prepend("<div id ='create_vessel_name_myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                                }, delayInMilliseconds);
                            }
                            return false;
                        }
                        else{
                            $('.has-error_myaccount').removeClass( "has-error_myaccount" )
                            $('#create_vessel_name_myAlert1').remove()
                            $('#create_vessel_name_myAlert2').remove()
                        }
                        // if ($("#vessel_name_id").val() === "") {
                        //     if (document.getElementById("fill_mandatory_fields")) {
                        //         if (document.getElementById('myAlert1')) {
                        //             if (document.getElementById('novesselname')) {
                        //                 document.getElementById('novesselname').innerHTML = "<strong><center>" + msg + "</center></strong>"
                        //             } else {
                        //                 document.getElementById('myAlert1').innerHTML = document.getElementById('myAlert1').innerHTML + "<div id='novesselname'><strong><center>" + msg1 + "</center></strong></div>"
                        //             }
                        //         } else {
                        //             $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><div id='novesselname'><strong><center>" + msg + "</center></strong></div></div>");
                        //         }
                        //     }
                        // }
                        // if ($("#vessel_flag_id").val() === "") {
                        //     if (document.getElementById("fill_mandatory_fields")) {
                        //         if (document.getElementById('myAlert1')) {
                        //             if (document.getElementById('novesselflag')) {
                        //                 document.getElementById('novesselflag').innerHTML = "<strong><center>" + msg + "</center></strong>"
                        //             } else {
                        //                 document.getElementById('myAlert1').innerHTML = document.getElementById('myAlert1').innerHTML + "<div id='novesselflag'><strong><center>" + msg2 + "</center></strong></div>"
                        //             }
                        //         } else {
                        //             $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><div id='novesselflag'><strong><center>" + msg + "</center></strong></div></div>");
                        //         }
                        //     }
                        // }
                        ev.stopPropagation();
                    } else {
                         openerp.jsonRpc('/create_new_vessel_name', 'call', {
                            'vessel_name': $modal.find("input[name='create_vessel_name']").val(),
                            'vessel_flag': $modal.find("input[name='create_vessel_flag']").val(),
                            'imo_number': $modal.find("input[name='create_imo_number']").val(),
                            'vessel_type_id': document.getElementById('vessel_type_select_id').options[document.getElementById('vessel_type_select_id').selectedIndex].value,
                            'vessel_nrt': $modal.find("input[name='create_vessel_nrt']").val(),
                            'vessel_crew': $modal.find("input[name='create_vessel_crew']").val(),
                             context: _.extend(openerp.website.get_context())
                        }).then(function (result) {
                            if (result == true){
                                // put vessel_name_id value from create new vessel form into vessel_name_select_id
                                $("#vessel_name_select_id").val($('#vessel_name_id').val());
                                $("#imo").val($('#imo_number_id').val());
                                $("#signup_vessel_type").val($("#vessel_type_select_id").val())
                                $("#new_vessel_flag").val("1");
                                $('#modal_create_new_vessel').remove();
                                for (i=0; i<document.getElementsByClassName('modal-backdrop fade in').length; i++ ) {
                                    document.getElementsByClassName('modal-backdrop fade in')[i].removeAttribute('class')
                                }
                            }
                            else {
                                var msg1 = "Vessel Name already exists in the database<br>Please Use the Autocomplete feature!";
                                if (document.getElementById("fill_mandatory_fields")) {
                                    if (document.getElementById('myAlert1')) {
                                        if (document.getElementById('cannotcreatevesselname')) {
                                            document.getElementById('cannotcreatevesselname').innerHTML = "<strong><center>" + msg1 + "</center></strong>"
                                        } else {
                                            document.getElementById('myAlert1').innerHTML = document.getElementById('myAlert1').innerHTML + "<div id='cannotcreatevesselname'><strong><center>" + msg1 + "</center></strong></div>"
                                        }
                                    } else {
                                        $('#fill_mandatory_fields').append("<div id ='myAlert1' class ='alert alert-danger'><div id='cannotcreatevesselname'><strong><center>" + msg1 + "</center></strong></div></div>");
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

function close_create_vessel_form(ev) {
    $('#modal_create_new_vessel').remove();
    for (i=0; i<document.getElementsByClassName('modal-backdrop fade in').length; i++ ) {
        document.getElementsByClassName('modal-backdrop fade in')[i].removeAttribute('class')
    }
}

function hide_show_create_and_edit_vessel_name_signup() {
    if (document.getElementById('vessel_name_select_id').value === 'CREATE..') {
        var vessel_name = $('#vessel_name_select_id').val()
        create_new_vessel(true, vessel_name);
    }
//        $('#vessel_name_id').attr('required', 'required').show();
//        $('#imo_number_id').attr('required', 'required').show();
//        $('#vessel_type_select_id').attr('required', 'required').show();
//        $('#vessel_nrt_id').attr('required', 'required').show();
//        $('#vessel_flag_id').attr('required', 'required').show();
//        $('#vessel_crew_id').attr('required', 'required').show();
//        $('#vname_filler1').show();
//        $('#vname_filler2').show();
//        $('#vname_filler3').show();
//        $('#vname_filler4').show();
//        $('#vname_filler5').show();
//        $('#vname_filler6').show();
//
//        $('#vessel_id').click(function () {
//            if (document.getElementById('vessel_name_select_id').value === "CREATE AND EDIT..") {
//                $('#vessel_name_id').show();
//                $('#imo_number_id').show();
//                $('#vessel_type_select_id').show();
//                $('#vessel_nrt_id').show();
//                $('#vessel_flag_id').show();
//                $('#vessel_crew_id').show();
//                $('#vname_filler1').show();
//                $('#vname_filler2').show();
//                $('#vname_filler3').show();
//                $('#vname_filler4').show();
//                $('#vname_filler5').show();
//                $('#vname_filler6').show();
//            } else {
//                $('#vessel_name_id').hide();
//                $('#imo_number_id').hide();
//                $('#vessel_type_select_id').hide();
//                $('#vessel_nrt_id').hide();
//                $('#vessel_flag_id').hide();
//                $('#vessel_crew_id').hide();
//                $('#vname_filler1').hide();
//                $('#vname_filler2').hide();
//                $('#vname_filler3').hide();
//                $('#vname_filler4').hide();
//                $('#vname_filler5').hide();
//                $('#vname_filler6').hide();
//            }
//        });
//    } else{
//        $('#vessel_name_id').removeAttr('required').hide();
//        $('#imo_number_id').removeAttr('required').hide();
//        $('#vessel_type_select_id').removeAttr('required').hide();
//        $('#vessel_nrt_id').removeAttr('required').hide();
//        $('#vessel_flag_id').removeAttr('required').hide();
//        $('#vessel_crew_id').removeAttr('required').hide();
//        $('#vname_filler1').hide();
//        $('#vname_filler2').hide();
//        $('#vname_filler3').hide();
//        $('#vname_filler4').hide();
//        $('#vname_filler5').hide();
//        $('#vname_filler6').hide();
//    }
}


(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};

    $('.create-account, .sign-in').click(function (ev) {
    // ev.preventDefault();
    if ($("input[name='password']").val().length<6){
         alert('New Passwords must be at least 6 characters in length.');
         return false;
        }
    if ($("input[name='password']").val() != $("input[name='confirm_password']").val()){
         alert('The passwords do not match!');
         return false;
        }
    })
    $('.oe_signup_form').each(function () {
        $('#imo').on('change', function(ev){
            if (this.value != null) {
                $('#call_sign').removeAttr('required');
            }
            else{
                $('#call_sign').attr('required', 'required')

            }
        });
        $('#call_sign').on('change', function(ev){
            if (this.value != null) {
                $('#imo').removeAttr('required');
            }
            else {
                $('#imo').attr('required', 'required')
            }
        });

        if (document.getElementById('vessel_name_select_id')) {
            const vess_nam = document.getElementById('vessel_name_select_id');
            vess_nam.addEventListener('change', hide_show_create_and_edit_vessel_name_signup());
            vess_nam.addEventListener('input', hide_show_create_and_edit_vessel_name_signup());
            vess_nam.addEventListener('click',
                openerp.jsonRpc('/myaccounts/get_vessel_name')
                    .then(function (data) {
                        var data_dict = JSON.parse(data);
                        var vessel_names = data_dict['vessel_name'];
                            autocomplete_substring_with_length_signup(document.getElementById("vessel_name_select_id"),
                            vessel_names, 2,
                            {'must_show': ['CREATE..']});
                        hide_show_create_and_edit_vessel_name_signup();
            }));
            $('#vessel_name_select_id').keyup(function () {
                var vess_namtypingTimer2;
                var vess_namtypingTimer2Interval2 = 1000
                clearTimeout(vess_namtypingTimer2);
                vess_namtypingTimer2 = setTimeout(hide_show_create_and_edit_vessel_name_signup, vess_namtypingTimer2Interval2);
            });
        }

    })


    $('.oe_signup_form').each(function () {
//        $('#vessel_name_select_id').on('change', function(ev){
//            if (this.value == "CREATE AND EDIT..") {
//                $('#vessel_name_id').attr('required', 'required')
//                $('#imo_number_id').attr('required', 'required')
//                $('#vessel_type_select_id').attr('required', 'required')
//                $('#vessel_nrt_id').attr('required', 'required')
//                $('#vessel_flag_id').attr('required', 'required')
//                $('#vessel_crew_id').attr('required', 'required')
//                // $('#shipping_agent_select_id').attr('required', 'required')
//            }
//            else{
//                $('#vessel_name_id').removeAttr('required');
//                $('#imo_number_id').removeAttr('required');
//                $('#vessel_type_select_id').removeAttr('required');
//                $('#vessel_nrt_id').removeAttr('required');
//                $('#vessel_flag_id').removeAttr('required');
//                $('#vessel_crew_id').removeAttr('required');
//                // $('#shipping_agent_select_id').removeAttr('required');
//
//            }
//        });
        $('#call_sign').on('change', function(ev){
            if (this.value != null) {
                $('#imo').removeAttr('required');
            }
            else {
                $('#imo').attr('required', 'required')
            }
        });
    })

    if (window.location.pathname.includes('/web/reset_password')) {
        var notes = document.getElementsByClassName('notes')
        for (var i=0;i<notes.length;i++){
            document.getElementsByClassName('notes')[i].style.bottom = "0px"
        }
    }

    if (document.getElementsByClassName('signup_error_msg')){
        var content = "Looks like you already have an account with us. Would you like to " + "<a href='/web/login' style='text-decoration: underline;'>log in</a>" +  " or " +  "<a href='/web/reset_password' style='text-decoration: underline;'>recover your password</a>" + "?"
        $('.signup_error_msg').replaceWith('<p class="signup_error_msg" style="color:red">' + content + '</p>')
    }
    if (document.getElementsByClassName('chandler_signup_error_msg')){
        var content = "Looks like you already have an account with us. Would you like to " + "<a href='/web/login' style='text-decoration: underline;'>log in</a>" +  " or " +  "<a href='/web/reset_password' style='text-decoration: underline;'>recover your password</a>" + "?"
        $('.chandler_signup_error_msg').replaceWith('<p class="chandler_signup_error_msg" style="color:red">' + content + '</p>')
    }

//        if (window.location.pathname.includes('/web/signup')) {
//     if (document.getElementById("vessel_name_select_id")) {
//         // if (optionExists('CREATE AND EDIT..', document.getElementById('vessel_name_select_id')) == false) {
//         //     var create_and_edit = document.getElementById("vessel_name_select_id");
//         //     var option = document.createElement("option");
//         //     option.text = "CREATE AND EDIT..";
//         //     create_and_edit.add(option, document.getElementById("vessel_name_select_id").length);
//         // }
//
//         $('#vessel_name_select_id').click(function () {
//             if (document.getElementById("vessel_name_select_id").options[document.getElementById("vessel_name_select_id").selectedIndex].text == "CREATE AND EDIT..") {
//                 $('#vessel_name_id').show();
//                 $('#imo_number_id').show();
//                 $('#vessel_type_select_id').show();
//                 $('#vessel_nrt_id').show();
//                 $('#vessel_flag_id').show();
//                 $('#vessel_crew_id').show();
//                 // $('#shipping_agent_select_id').show();
//             } else {
//                 $('#vessel_name_id').hide();
//                 $('#imo_number_id').hide();
//                 $('#vessel_type_select_id').hide();
//                 $('#vessel_nrt_id').hide();
//                 $('#vessel_flag_id').hide();
//                 $('#vessel_crew_id').hide();
//                 // $('#shipping_agent_select_id').hide();
//             }
//         });
//     }
//     }

})();




function show_hide_buttons () {
    $('#vessel_name_id').hide();
    $('#imo_number_id').hide();
    $('#vessel_type_select_id').hide();
    $('#vessel_nrt_id').hide();
    $('#vessel_flag_id').hide();
    $('#vessel_crew_id').hide();
    // $('#shipping_agent_select_id').hide();
}
try {
    window.onload = show_hide_buttons();
}
catch (err) {
    null;
}