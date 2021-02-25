function show_hide_buttons () {
    $('#vessel_name_id').hide();
    $('#imo_number_id').hide();
    $('#vessel_type_select_id').hide();
    $('#vessel_nrt_id').hide();
    $('#vessel_flag_id').hide();
    $('#vessel_crew_id').hide();
    $('#shipping_agent_select_id').hide();
    $('#vname_filler1').hide();
    $('#vname_filler2').hide();
    $('#vname_filler3').hide();
    $('#vname_filler4').hide();
    $('#vname_filler5').hide();
    $('#vname_filler6').hide();
}
try {
    window.onload = show_hide_buttons();
}
catch (err) {
    null;
}

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
function passwordChanged() {
    var strength = document.getElementById('strength');
    var strongRegex = new RegExp("^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
    var mediumRegex = new RegExp("^(?=.{7,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
    var enoughRegex = new RegExp("(?=.{6,}).*", "g");
    var pwd = document.getElementById("new_password");
    if (pwd.value.length==0) {
    // strength.innerHTML = 'Type Password';
    } else if (false == enoughRegex.test(pwd.value)) {
    strength.innerHTML = 'More Characters';
    } else if (strongRegex.test(pwd.value)) {
    strength.innerHTML = '<span style="color:green">Strong!</span>';
    } else if (mediumRegex.test(pwd.value)) {
    strength.innerHTML = '<span style="color:orange">Medium!</span>';
    } else {
    strength.innerHTML = '<span style="color:red">Weak!</span>';
    }
}

function getValueWithNewVesselName(newVesselName){
    if (newVesselName) {
        pageData = {
            'email': document.getElementById("email").value,
            'vname': document.getElementById("vessel_name_autocomplete").value,
            'vessel_name_id': document.getElementById("vessel_name_id").value.toUpperCase(),
            'imo_number_id': document.getElementById("imo_number_id").value,
            'vessel_type_select_id': document.getElementById("vessel_type_select_id").value,
            'vessel_nrt_id': document.getElementById("vessel_nrt_id").value,
            'vessel_flag_id': document.getElementById("vessel_flag_id").value,
            'vessel_crew_id': document.getElementById("vessel_crew_id").value,
            // 'shipping_agent_select_id': document.getElementById("shipping_agent_select_id").value,
            'vtype': document.getElementById("vessel_id").value,
            'name': document.getElementById("name").value,
            'tel': document.getElementById("tel").value,
            'imo': document.getElementById("imo").value,
            'call_sign': document.getElementById("call_sign").value,
            'pc_one': document.getElementById("chandler_autocomplete_id1").value,
            'pc_two': document.getElementById("chandler_autocomplete_id2").value,
            'pc_three': document.getElementById("chandler_autocomplete_id3").value,
            context: _.extend(openerp.website.get_context())

        };
        return pageData
    }
    else {
        pageData = {
            'email': document.getElementById("email").value,
            'vname': document.getElementById("vessel_name_autocomplete").value,
            'vtype': document.getElementById("vessel_id").value,
            'name': document.getElementById("name").value,
            'tel': document.getElementById("tel").value,
            'imo': document.getElementById("imo").value,
            'call_sign': document.getElementById("call_sign").value,
            'pc_one': document.getElementById("chandler_autocomplete_id1").value,
            'pc_two': document.getElementById("chandler_autocomplete_id2").value,
            'pc_three': document.getElementById("chandler_autocomplete_id3").value,
            context: _.extend(openerp.website.get_context()),

        };
        return pageData
    }
}

(function() {
    'use strict';
    var website = openerp.website;
    website.openerp_website = {};

    if (document.getElementById('myaccount_leftsidebar')) {
        if (window.location.pathname=="/myaccounts") {
            $('#myaccount_leftsidebar').addClass('active');
            $('#myenquiry_leftsidebar').removeClass('active');
        }
    }

    if (document.getElementById('myenquiry_leftsidebar')) {
        if (window.location.pathname=="/myenquiry") {
            $('#myenquiry_leftsidebar').addClass('active');
            $('#myaccount_leftsidebar').removeClass('active');
            $('#edit_profile2').hide()
            $('.edit-profile>h2').css({position: 'relative', top: '15px'})
        }
    }


    var check_mode = function (view_id, mode) {
        $('#myinfo_detail').find('input,textarea,select').each(function () {
                if (mode == 'edit'){
                     this.classList.remove('no-border-no-shadow');
                    this.disabled = false
                }
                else {
                    this.classList.add('no-border-no-shadow');
                    this.disabled = true;
                };
        })
    }



    if ($('#myinfo_detail').length) {
        check_mode(this, 'read');
        $('#save_profile').hide();
        $('#edit_profile').show();
    };




    $('#myinfo_detail').each(function () {
        // if (document.getElementById('imo').value!="") {
        //     $('#call_sign').removeAttr('required');
        // }
        // else{
        //     $('#call_sign').attr('required', 'required')
        //
        // }
        //
        // if (document.getElementById('call_sign').value!="") {
        //     $('#imo').removeAttr('required');
        // }
        // else {
        //     $('#imo').attr('required', 'required')
        // }
        // var self = this
        //
        // $('#imo').on('change', function(ev){
        //     if (this.value != null) {
        //         $('#call_sign').removeAttr('required');
        //     }
        //     else{
        //         $('#call_sign').attr('required', 'required')
        //
        //     }
        // });
        // $('#call_sign').on('change', function(ev){
        //     if (this.value != null) {
        //         $('#imo').removeAttr('required');
        //     }
        //     else {
        //         $('#imo').attr('required', 'required')
        //     }
        // });

        // if (document.getElementById("vessel_name_select_id")) {
        //         if (optionExists( 'CREATE AND EDIT..', document.getElementById( 'vessel_name_select_id' ) ) == false) {
        //             var create_and_edit = document.getElementById("vessel_name_select_id");
        //             var option = document.createElement("option");
        //             option.text = "CREATE AND EDIT..";
        //             create_and_edit.add(option, document.getElementById("vessel_name_select_id").length);
        //         }
        //
        //         $('#vessel_id').click(function () {
        //             if (document.getElementById("vessel_id").options[document.getElementById("vessel_name_select_id").selectedIndex].text == "CREATE AND EDIT..") {
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
        // }

        if (document.getElementById('email')) {
        document.getElementById('email').disabled = true;
        document.getElementById('email').setAttribute('style', 'background-color:#fff;');
        }
        if (document.getElementById('vessel_name')) {
            document.getElementById('vessel_name').disabled = true;
            document.getElementById('vessel_name').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('vessel_id')) {
            document.getElementById('vessel_id').disabled = true;
            document.getElementById('vessel_id').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('name')) {
            document.getElementById('name').disabled = true;
            document.getElementById('name').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('tel')) {
            document.getElementById('tel').disabled = true;
            document.getElementById('tel').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('imo')) {
            document.getElementById('imo').disabled = true;
            document.getElementById('imo').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('call_sign')) {
            document.getElementById('call_sign').disabled = true;
            document.getElementById('call_sign').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('pc_one')) {
            document.getElementById('pc_one').disabled = true;
            document.getElementById('pc_one').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('pc_two')) {
            document.getElementById('pc_two').disabled = true;
            document.getElementById('pc_two').setAttribute('style', 'background-color:#fff;');
        }

        if (document.getElementById('pc_three')) {
            document.getElementById('pc_three').disabled = true;
            document.getElementById('pc_three').setAttribute('style', 'background-color:#fff;');
        }

        // if (document.getElementById('vessel_name_autocomplete')) {
        //     const vess_nam = document.getElementById('vessel_name_autocomplete');
        //     vess_nam.addEventListener('change', hide_show_create_and_edit_vessel_name());
        //     vess_nam.addEventListener('input', hide_show_create_and_edit_vessel_name());
        //     vess_nam.addEventListener('click',
        //         openerp.jsonRpc('/myaccounts/get_vessel_name')
        //             .then(function (data) {
        //                 var data_dict = JSON.parse(data);
        //                 var vessel_names = data_dict['vessel_name'];
        //                 autocomplete_substring_with_length(document.getElementById("vessel_name_autocomplete"),
        //                     vessel_names, 2,
        //                     {'must_show': ['CREATE AND EDIT..']});
        //                 hide_show_create_and_edit_vessel_name();
        //             })
        //     )
        // }

        $(self).on('click', '#show_profile', function(ev){
            $('#myinfo_detail').css('display', 'block');
            $('#myenquiry').css('display', 'none');
        });

        $(self).on('click', '#show_enquiry', function(ev){
            $('#myinfo_detail').css('display', 'none');
            $('#myenquiry').css('display', 'block');
        });

        $('#change_password').click(function(event) {
            event.preventDefault();
            var pathname = window.location.pathname;
            var $form = $('#myinfo_title');
            openerp.jsonRpc('/changepassword', 'call', {
                       context: _.extend({'open_form': 'True'}, openerp.website.get_context())
                    }).then(function (modal) {
                        self = this;

                        var $modal = $(modal);
                        $modal.appendTo($form)
                        .modal()
                        .on('hidden.bs.modal', function () {
                            $(this).remove();
                        });

                        // Event on change password pop-ip
                        $('.oe_form_button_cancel').click(function () {
                            $modal.modal('hide');
                        })

                        $("input[name='confirm_pwd']").change(function () {
                            var confirm_pass = $("input[name='confirm_pwd']").val();
                            if (confirm_pass.length >= 1)
                            {
                             var new_pass = $("input[name='new_password']").val();
                             if (confirm_pass != new_pass){
                               $("input[name='confirm_pwd']").val(null)
                               alert('Confirm Password does not match!')  ;
                             };
                            };

                        })

                        $('.change_password').click(function (ev) {
                            ev.preventDefault();
                            if ($("input[name='new_password']").val().length<6){
                                 alert('New Passwords must be at least 6 characters in length.');
                                 return false;
                            }
                            if (!$modal.find("input[name='old_pwd']").val() && !$("input[name='new_password']").val()) {
                                return
                            }
                             openerp.jsonRpc('/changepassword', 'call', {
                                'old_password': $modal.find("input[name='old_pwd']").val(),
                                'new_password': $modal.find("input[name='new_password']").val(),
                                 context: _.extend(openerp.website.get_context())
                            }).then(function (result) {
                                if (result == true){
                                window.location.pathname = pathname;
                                }
                                else {
                                    var $modal = $(result);
                                    $modal.appendTo($form)
                                        .modal()
                                        .on('hidden.bs.modal', function () {
                                            $(this).remove();
                                        });
                                }
                             })
                        })

            })

        });




    });

    if (document.getElementById('edit_profile') || document.getElementById('edit_profile2')) {
        $('#edit_profile, #edit_profile2').click(function () {
            $('#myinfo_detail').each(function () {
                $('#save_profile').show();
                $('#save_profile').prop('type', 'submit')
                $('#edit_profile').hide();
                $('#edit_profile2').hide();
                var mode = 'edit';
                check_mode(this, mode);

            })
            //
            // $('#email').removeClass('no-border-no-shadow');
            // $('#vname').removeClass('no-border-no-shadow');
            // $('#vessel_id').removeClass('no-border-no-shadow');
            // $('#name').removeClass('no-border-no-shadow');
            // $('#tel').removeClass('no-border-no-shadow');
            // $('#imo').removeClass('no-border-no-shadow');
            // $('#call_sign').removeClass('no-border-no-shadow');
            // $('#pc_one').removeClass('no-border-no-shadow');
            // $('#pc_two').removeClass('no-border-no-shadow');
            // $('#pc_three').removeClass('no-border-no-shadow');
            // document.getElementById('email').disabled = false;
            // document.getElementById('vname').disabled = false;
            // document.getElementById('vessel_id').disabled = false;
            // document.getElementById('name').disabled = false;
            // document.getElementById('tel').disabled = false;
            // document.getElementById('imo').disabled = false;
            // document.getElementById('call_sign').disabled = false;
            // document.getElementById('pc_one').disabled = false;
            // document.getElementById('pc_two').disabled = false;
            // document.getElementById('pc_three').disabled = false;


        });
    }

    if (document.getElementById('save_profile')) {
        $('#save_profile').click(function () {
            var required_fields = document.querySelectorAll('[required="required"]'),i;
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
                if (!document.getElementById('myaccount_myAlert1')){
                    var msg = '<p>Please fill up the mandatory fields in asterisk (*)</p>\n';
                    var delayInMilliseconds = 100;
                    setTimeout(function() {
                        $('#myaccount_note').prepend("<div id ='myaccount_myAlert1' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                        $('.col-12.text-right').append("<div id ='myaccount_myAlert2' class ='alert alert-danger'><strong><center>" + msg + "</center></strong></div>");
                    }, delayInMilliseconds);
                }
                return false;
            }
            else{
                $('.has-error_myaccount').removeClass( "has-error_myaccount" )
                $('#myaccount_myAlert1').remove()
                $('#myaccount_myAlert2').remove()
            }

            if (document.getElementById("vessel_name_autocomplete").value != '' &&
                document.getElementById("vessel_name_autocomplete").value != 'CREATE AND EDIT..'){
                openerp.jsonRpc('/_website_myaccount/check_vessel_name', 'call' , {value:document.getElementById("vessel_name_autocomplete").value})
                    .then(function (o) {
                        var data = JSON.parse(o);
                        // alert (data)
                        if (data == false){
                            alert("Vessel Name: " + document.getElementById("vessel_name_autocomplete").value +
                                "\n Cannot Find in the system");
                            $('#save_profile').show();

                            var mode = 'edit';
                            check_mode(this, mode);
                            $('#edit_profile').hide();
                            $('#edit_profile2').hide();
                            return false;

                        }

                        // check if entered chandler is in approved list
                        // names in matches list are names found in database


            } )
            }

            // $('#email').addClass('no-border-no-shadow');
            // $('#vname').addClass('no-border-no-shadow');
            // $('#vessel_id').addClass('no-border-no-shadow');
            // $('#name').addClass('no-border-no-shadow');
            // $('#tel').addClass('no-border-no-shadow');
            // $('#imo').addClass('no-border-no-shadow');
            // $('#call_sign').addClass('no-border-no-shadow');
            // $('#pc_one').addClass('no-border-no-shadow');
            // $('#pc_two').addClass('no-border-no-shadow');
            // $('#pc_three').addClass('no-border-no-shadow');
            // document.getElementById('email').disabled = true;
            // document.getElementById('vname').disabled = true;
            // document.getElementById('vessel_id').disabled = true;
            // document.getElementById('name').disabled = true;
            // document.getElementById('tel').disabled = true;
            // document.getElementById('imo').disabled = true;
            // document.getElementById('call_sign').disabled = true;
            // document.getElementById('pc_one').disabled = true;
            // document.getElementById('pc_two').disabled = true;
            // document.getElementById('pc_three').disabled = true;

            // $('#myinfo_detail').each(function () {



            $('#save_profile').hide();

            var mode = 'read';
            check_mode(this, mode);
            $('#edit_profile').show();
            $('#edit_profile2').show();

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

                            if (confirm(msg)) {
                                var param = {
                                        'email': document.getElementById("email").value,
                                        'vname': document.getElementById("vessel_name_autocomplete").value,
                                        'vtype': document.getElementById("vessel_id").value,
                                        'name': document.getElementById("name").value,
                                        'tel': document.getElementById("tel").value,
                                        'imo': document.getElementById("imo").value,
                                        'call_sign': document.getElementById("call_sign").value,
                                        context: _.extend(openerp.website.get_context()),
                                };
                                if (conditional_flag1 === false && pc_one !== "" && matches.includes(pc_one)) {param['pc_one']=pc_one}
                                if (conditional_flag2 === false && pc_two !== "" && matches.includes(pc_two)) {param['pc_two']=pc_two}
                                if (conditional_flag3 === false && pc_three !== "" && matches.includes(pc_three)) {param['pc_three']=pc_three}
                                openerp.jsonRpc('/_website_myaccount/_update_account_info', 'call', param)
                                window.location.replace("/myaccounts")
                            } else {
                                //do nothing
                            }
                        } else {
                            if (document.getElementById("vessel_name_autocomplete").value == "CREATE AND EDIT.."){
                                var newVesselName = true;
                                openerp.jsonRpc('/_website_myaccount/_update_account_info', 'call', {
                                value:getValueWithNewVesselName(newVesselName)
                             }).then(function(val){
                                        if (val){
                                            location.reload(true);

                                        }
                                    }

                                )}
                            else{var newVesselName = false;
                                openerp.jsonRpc('/_website_myaccount/_update_account_info', 'call', {
                                    value:getValueWithNewVesselName(newVesselName)
                            })}

                        }

                    }
                );

            }



            //     .then(function () {
            //     alert("SUCCESSSSSSSSSSSSSS");
            // }).fail(function () {
            //     alert("FAILLLLLLLLLLLLLLL");
            // });
            // $.ajax({  type: "POST",
            //                 url: "/_website_myaccount/_update_account_info",
            //                 data: {
            //                         'email': document.getElementById("email").value,
            //                         'vname': document.getElementById("vname").value,
            //                         'vtype': document.getElementById("vtype").value,
            //                         'name': document.getElementById("name").value,
            //                         'tel': document.getElementById("tel").value,
            //                         'imo': document.getElementById("imo").value,
            //                         'call_sign': document.getElementById("call_sign").value,
            //                         'pc_one': document.getElementById("pc_one").value,
            //                         'pc_two': document.getElementById("pc_two").value,
            //                         'pc_three': document.getElementById("pc_three").value,
            // }});
            // });
        });
    }

})();

function hide_show_create_and_edit_vessel_name() {
    if (document.getElementById('vessel_name_autocomplete').value === 'CREATE AND EDIT..') {
        $('#vessel_name_id').attr('required', 'required').show();
        $('#imo_number_id').attr('required', 'required').show();
        $('#vessel_type_select_id').attr('required', 'required').show();
        $('#vessel_nrt_id').attr('required', 'required').show();
        $('#vessel_flag_id').attr('required', 'required').show();
        $('#vessel_crew_id').attr('required', 'required').show();
        $('#vname_filler1').show();
        $('#vname_filler2').show();
        $('#vname_filler3').show();
        $('#vname_filler4').show();
        $('#vname_filler5').show();
        $('#vname_filler6').show();

        $('#vessel_id').click(function () {
            if (document.getElementById('vessel_name_autocomplete').value === "CREATE AND EDIT..") {
                $('#vessel_name_id').show();
                $('#imo_number_id').show();
                $('#vessel_type_select_id').show();
                $('#vessel_nrt_id').show();
                $('#vessel_flag_id').show();
                $('#vessel_crew_id').show();
                $('#vname_filler1').show();
                $('#vname_filler2').show();
                $('#vname_filler3').show();
                $('#vname_filler4').show();
                $('#vname_filler5').show();
                $('#vname_filler6').show();
            } else {
                $('#vessel_name_id').hide();
                $('#imo_number_id').hide();
                $('#vessel_type_select_id').hide();
                $('#vessel_nrt_id').hide();
                $('#vessel_flag_id').hide();
                $('#vessel_crew_id').hide();
                $('#vname_filler1').hide();
                $('#vname_filler2').hide();
                $('#vname_filler3').hide();
                $('#vname_filler4').hide();
                $('#vname_filler5').hide();
                $('#vname_filler6').hide();
            }
        });
    } else{
        $('#vessel_name_id').removeAttr('required').hide();
        $('#imo_number_id').removeAttr('required').hide();
        $('#vessel_type_select_id').removeAttr('required').hide();
        $('#vessel_nrt_id').removeAttr('required').hide();
        $('#vessel_flag_id').removeAttr('required').hide();
        $('#vessel_crew_id').removeAttr('required').hide();
        $('#vname_filler1').hide();
        $('#vname_filler2').hide();
        $('#vname_filler3').hide();
        $('#vname_filler4').hide();
        $('#vname_filler5').hide();
        $('#vname_filler6').hide();
    }
}

function autocomplete_substring_with_length(inp, arr, leng, context={}) {
    /*
    context = {'must_show': array}
     */
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
      this.parentNode.appendChild(a);
      /*for each item in the array...*/
      if (val.length >= leng) {
          for (i = 0; i < prev_leng; i++) {
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
                      hide_show_create_and_edit_vessel_name();
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