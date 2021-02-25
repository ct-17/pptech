$(document).ready(function () {
        if (window.location.href.includes("/shop?DropdownCategory")) {
            $('.left-sidebar').find('a').each(function () {
                var index = this.href.indexOf("?search");
                if (index !== -1) {
                    this.href = this.href.substring(0, index);
                }
            })
        }

        if (document.getElementById('submit_button1')) {
            $('#submit_button1').click(function () {
                document.getElementById('chandler_checkbox1').checked = false;
                if (document.getElementById('chandler_autocomplete_id1').value !== "") {
                    document.getElementById('chandler_checkbox1').checked = true;
                }
            });
        }
        if (document.getElementsByClassName('js_quantity').length>= 1){
            var js_qty = document.getElementsByClassName('js_quantity')
            for (var i=0; i<js_qty.length;i++){
                js_qty[i].onkeypress = function(e) {
                e = e || window.event;
                var charCode = (typeof e.which == "undefined") ? e.keyCode : e.which;
                var charStr = String.fromCharCode(charCode);
                if (/\D/.test(charStr)) {
                    return false;
                }
                }
                js_qty[i].onkeyup=function numberMobile(e){
                    e.target.value = e.target.value.replace(/[^\d]/g,'');
                    return false;
                }
            };
        }
        function check_if_out_of_stock(){
            if ($('.insufficient_stock:visible').length>0) {
                    event.preventDefault();
            }
        }

        if (window.location.pathname.includes('/shop/cart') || window.location.pathname.includes('/shop/checkout')) {
            if( $('#process_checkout').length ){
                document.getElementById("process_checkout").addEventListener("click", check_if_out_of_stock)
            }
            if($('#review_enquiry_link')){
                $('#review_enquiry_link').bind('click', function() {
                    setTimeout(function() {
                        window.location.href = "/shop/cart";
                    }, 400);

                });
            }
        }
        if (window.location.pathname.includes('/shop/checkout')) {
            var timesRun = 0;
            var interval = setInterval(function(){
                timesRun += 1;
                if(timesRun === 15){
                    clearInterval(interval);
                }
                $( ".cart-quantity" ).load(window.location.href + " .cart-quantity" );
            }, 1000);
        }

        if (document.getElementById('myenquiry'))
        {
            if ($('#myenquiry .js_quantity').length>0){
                for (var i=0;i<$('#myenquiry .js_quantity').length;i++){
                    if($('#myenquiry .js_quantity')[i].value == 1 && $('#myenquiry .js_quantity')[i].attributes.getNamedItem('value-max').value == 1){
                        $('#myenquiry .js_quantity')[i].closest('.oe_website_spinner').getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                        $('#myenquiry .js_quantity')[i].readOnly = true;
                    }
                }
            }
            // Qty plus button on click check stock prompt
            $(".fa-plus").on('click', function () {
                var input_qty = $(this).closest('div').find('input')[0];
                var val = input_qty.value;
                var $input = $($(this).closest('div').find('input'));
                var parent = $(this).closest('.myenquiry_so');
                var confirm = parent.find('.myenquiry_confirm')
                if (val == 1) {
                    input_qty.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                }
                if (input_qty.attributes.getNamedItem('value-max') != null) {
                    if (val != 1) {
                        input_qty.offsetParent.getElementsByTagName('a')[0].classList.remove('disabled')
                        input_qty.offsetParent.getElementsByTagName('a')[0].classList.add('js_add_cart_json')
                    }
                    // // Disable the plus button when qty reaches max stock
                    // if (parseInt(val) + 1 == parseInt(input_qty.attributes.getNamedItem('value-max').value)){
                    //     input_qty.offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                    // }
                    if (parseInt(input_qty.attributes.getNamedItem('value-max').value) <= parseInt(val)) {
                        $(input_qty).closest('td').find('.insufficient_stock').css({"display": "block"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "19px"});
                        $input.data('update_change', false);
                        $input.val(parseInt(val)-1).change();
                        confirm.addClass("myenquiry_confirm_disabled")
                        confirm.prop('disabled',true);
                        this.offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                        // Disable the minus button when qty = 1
                        // if (input_qty.defaultValue == 1) {
                        //     input_qty.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                        // }
                    } else {
                        $(input_qty).closest('td').find('.insufficient_stock').css({"display": "none"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "unset"});
                        this.offsetParent.getElementsByTagName('a')[1].classList.remove('disabled')
                        if (! parent.find('.insufficient_stock').is(":visible")){
                            confirm.removeClass("myenquiry_confirm_disabled")
                            confirm.addClass("myenquiry_confirm_enabled")
                        }
                    }
                }
            });

            // Qty input field key up check stock prompt
            $("input:text[class^='js_quantity form-control']").on('keyup', function () {
                var val = this.value;
                var $input = $(this);
                var parent = $(this).closest('.myenquiry_so');
                var confirm = parent.find('.myenquiry_confirm')
                if (val < 1) {
                    alert('Your ADD TO CART quantity is less than minimum order limit. Please make sure the quantity is at least 1.')
                    $input.data('update_change', false);
                    $input.val(this.defaultValue).change();
                    if (this.defaultValue == 1) {
                        this.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                    }
                    val = this.defaultValue
                }
                if (val == 1) {
                    this.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                }
                if (this.attributes.getNamedItem('value-max') != null) {
                    if (val != 1) {
                        this.offsetParent.getElementsByTagName('a')[0].classList.remove('disabled')
                        this.offsetParent.getElementsByTagName('a')[0].classList.add('js_add_cart_json')
                    }
                    if (parseInt(this.attributes.getNamedItem('value-max').value) <= parseInt(val)) {
                        // $('#cart_instance').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + "Sorry, our stock is insufficient to fulfill your request on the following products:" + "<br/>" +
                        //     "<div style='text-align: left !important;text-indent: 18em !important;'>" + this.attributes.getNamedItem('product-name').value + "</div>" +
                        //     "</center></strong></div>");
                        $(this).closest('td').find('.insufficient_stock').css({"display": "block"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "19px"});
                        confirm.addClass("myenquiry_confirm_disabled")
                        confirm.prop('disabled',true);
                        this.offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                        $input.data('update_change', false);
                        // $input.val(this.defaultValue).change();
                        // Disable the minus button when qty = 1
                        // if (this.defaultValue == 1) {
                        //     this.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                        // }
                    } else {
                        $(this).closest('td').find('.insufficient_stock').css({"display": "none"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "unset"});
                        this.offsetParent.getElementsByTagName('a')[1].classList.remove('disabled')
                        if (! parent.find('.insufficient_stock').is(":visible")){
                            confirm.removeClass("myenquiry_confirm_disabled")
                            confirm.addClass("myenquiry_confirm_enabled")
                        }
                        var line_parent = $(this).closest('.cart_item');
                        var old_line_qty = line_parent.find('.line_qty').val()
                        var new_line_qty = line_parent.find('.js_quantity').val()
                        var diff = new_line_qty - old_line_qty
                        var line_price = parseFloat(line_parent.find('.oe_currency_value').text().replace(/,/g, ''))
                        var total = parseFloat(parent.find('.myenquiry_subtotal .oe_currency_value').text().replace(/,/g, ''))
                        var new_total = commaSeparateNumber((total + line_price * diff).toFixed(2))
                        parent.find('.myenquiry_subtotal .oe_currency_value').text(new_total)
                        line_parent.find('.line_qty').val(new_line_qty)
                    }
                }
            });
            if (document.getElementById('myinfo_enquiry')){
                if (document.getElementsByClassName('js_quantity')) {
                    var cart_qty = document.getElementsByClassName('js_quantity')
                    var cart_minus = document.getElementsByClassName('fa-minus')
                    for (i = 0; i<cart_qty.length; ++i) {
                        if (cart_qty[i].value == 1) {
                            cart_minus[i].parentElement.setAttribute("class", "disabled")
                        }
                    }
                }
            }
        }

        if (document.getElementById('cart_products'))
        {
            if ($('#cart_products .js_quantity').length>0){
                for (var i=0;i<$('#cart_products .js_quantity').length;i++){
                    if($('#cart_products .js_quantity')[i].value == 1 && $('#cart_products .js_quantity')[i].attributes.getNamedItem('value-max').value == 1){
                        $('#cart_products .js_quantity')[i].offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                        $('#cart_products .js_quantity')[i].readOnly = true;
                    }
                }
            }

            // Qty plus button on click check stock prompt
            $(".fa-plus").on('click', function () {
                var input_qty = $(this).closest('div').find('input')[0];
                var val = input_qty.value;
                var $input = $($(this).closest('div').find('input'));
                var parent = $(this).closest('.oe_cart');
                var confirm = parent.find('#process_checkout')
                if (val == 1) {
                    input_qty.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                }
                if (input_qty.attributes.getNamedItem('value-max') != null) {
                    if (val != 1) {
                        input_qty.offsetParent.getElementsByTagName('a')[0].classList.remove('disabled')
                        input_qty.offsetParent.getElementsByTagName('a')[0].classList.add('js_add_cart_json')
                    }
                    // // Disable the plus button when qty reaches max stock
                    // if (parseInt(val) + 1 == parseInt(input_qty.attributes.getNamedItem('value-max').value)){
                    //     input_qty.offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                    // }
                    if (parseInt(input_qty.attributes.getNamedItem('value-max').value) <= parseInt(val)) {
                        if (!$(input_qty).closest('td').find('.insufficient_stock').is(":visible")){
                            $(input_qty).closest('td').find('.insufficient_stock').css({"display": "block","position": "relative", "top": "25px"});
                            $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "27px"});
                            // $input.data('update_change', false);
                            // $input.val(parseInt(val)-1).change();
                            confirm.addClass("process_checkout_disabled")
                            $(this).css({"color": "#ddd", "cursor": "default"})
                            // this.offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                            // // Disable the minus button when qty = 1
                            // if (input_qty.defaultValue == 1) {
                            //     input_qty.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                            // }
                        }
                        else{
                            $input.val(parseInt(val)-1).change();
                            confirm.addClass("process_checkout_disabled")
                            $(this).css({"color": "#ddd", "cursor": "default"})
                        }

                    } else {
                        $(input_qty).closest('td').find('.insufficient_stock').css({"display": "none"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "unset"});
                        this.offsetParent.getElementsByTagName('a')[1].classList.remove('disabled')
                        $(this).css({"color": "#000", "cursor": "pointer"})
                        if (! parent.find('.insufficient_stock').is(":visible")){
                            if (confirm.hasClass("process_checkout_disabled")){
                                confirm.removeClass("process_checkout_disabled")
                                confirm.addClass("process_checkout_enabled")
                            }
                        }
                    }
                }
            });

            // Qty input field key up check stock prompt
            $("input:text[class^='js_quantity form-control']").on('keyup', function () {
                var val = this.value;
                var $input = $(this);
                var parent = $(this).closest('.oe_cart');
                var confirm = parent.find('#process_checkout')
                if (val < 1) {
                    alert('Your ADD TO CART quantity is less than minimum order limit. Please make sure the quantity is at least 1.')
                    $input.data('update_change', false);
                    $input.val(this.defaultValue).change();
                    if (this.defaultValue == 1) {
                        this.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                    }
                    val = this.defaultValue
                }
                if (val == 1) {
                    this.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                }
                if (this.attributes.getNamedItem('value-max') != null) {
                    if (val != 1) {
                        this.offsetParent.getElementsByTagName('a')[0].classList.remove('disabled')
                        this.offsetParent.getElementsByTagName('a')[0].classList.add('js_add_cart_json')
                    }
                    if (parseInt(this.attributes.getNamedItem('value-max').value) < parseInt(val)) {
                        // $('#cart_instance').prepend("<div id ='myAlert' class ='alert alert-danger' width='50%'><a href = '#' class = 'close' data-dismiss = 'alert'>&times;</a><strong><center>" + "Sorry, our stock is insufficient to fulfill your request on the following products:" + "<br/>" +
                        //     "<div style='text-align: left !important;text-indent: 18em !important;'>" + this.attributes.getNamedItem('product-name').value + "</div>" +
                        //     "</center></strong></div>");
                        $(this).closest('td').find('.insufficient_stock').css({"display": "block","position": "relative", "top": "25px"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "27px"});;
                        confirm.addClass("process_checkout_disabled")
                        $(this).closest('.oe_website_spinner').find('i').last().css({"color": "#ddd", "cursor": "default"});
                        $input.data('update_change', false);
                        if($(this)[0].value == 1 && $(this)[0].attributes.getNamedItem('value-max').value == 1){
                            $('this')[0].offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                        }
                        // $input.val(this.defaultValue).change();
                        // Disable the minus button when qty = 1
                        // if (this.defaultValue == 1) {
                        //     this.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                        // }
                    } else {
                        $(this).closest('td').find('.insufficient_stock').css({"display": "none"});
                        $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "unset"});
                        $(this).closest('.oe_website_spinner').find('i').last().css({"color": "#000", "cursor": "pointer"});
                        if (! parent.find('.insufficient_stock').is(":visible")){
                            if (confirm.hasClass("process_checkout_disabled")){
                                confirm.removeClass("process_checkout_disabled")
                                confirm.addClass("process_checkout_enabled")
                            }
                        }
                        if($(this)[0].value == 1 && $(this)[0].attributes.getNamedItem('value-max').value == 1){
                            $(this)[0].offsetParent.getElementsByTagName('a')[1].setAttribute('class', 'disabled')
                            $(this).closest('.oe_website_spinner').find('i').last().css({"color": "#ddd", "cursor": "default"})
                        }
                    }
                }
            });
            if (document.getElementById('myinfo_enquiry')){
                if (document.getElementsByClassName('js_quantity')) {
                    var cart_qty = document.getElementsByClassName('js_quantity')
                    var cart_minus = document.getElementsByClassName('fa-minus')
                    for (i = 0; i<cart_qty.length; ++i) {
                        if (cart_qty[i].value == 1) {
                            cart_minus[i].parentElement.setAttribute("class", "disabled")
                        }
                    }
                }
            }
        }



        // Cart qty Onclick
        if (document.getElementById('cart_products')){
            if (document.getElementsByClassName('js_quantity')) {
            var cart_qty = document.getElementsByClassName('js_quantity')
            var cart_minus = document.getElementsByClassName('fa-minus')
            var cart_plus = document.getElementsByClassName('fa-plus')

            function minus_onclick() {
                var that = this;
                var $input = $($(this).closest('div').find('input'));
                var input_qty = $(this).closest('div').find('input')[0];
                var val = input_qty.value;
                var parent = $(this).closest('.oe_cart');
                var confirm = parent.find('#process_checkout')
                if (this.offsetParent.getElementsByTagName('input')[0].value == 2) {
                    setTimeout(function () {
                        {
                            that.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                        }
                    }, 100);
                }
                // Remove insufficient quantity if exists
                // $(this).closest('td').find('#insufficient_stock').css({"display": "none"});

                if (parseInt(input_qty.attributes.getNamedItem('value-max').value) < parseInt(val)-1) {
                        $(input_qty).closest('td').find('.insufficient_stock').css({"display": "block"});
                        $input.data('update_change', false);
                        // $input.val(parseInt(val)-1).change();
                        confirm.addClass("process_checkout_disabled")
                        $(this).closest('.oe_website_spinner').find('i').last().css({"color": "#ddd", "cursor": "default"})
                        // Disable the minus button when qty = 1
                        // if (input_qty.defaultValue == 1) {
                        //     input_qty.offsetParent.getElementsByTagName('a')[0].setAttribute('class', 'disabled')
                        // }
                } else {
                    $(input_qty).closest('td').find('.insufficient_stock').css({"display": "none"});
                    $(this).closest('td').find('.qty-feild').css({"position": "relative", "top": "unset"});
                    this.offsetParent.getElementsByTagName('a')[1].classList.remove('disabled')
                    $(this).closest('.oe_website_spinner').find('i').last().css({"color": "#000", "cursor": "pointer"})
                    if (! parent.find('.insufficient_stock').is(":visible")){
                        if (! parent.find('.insufficient_stock').is(":visible")){
                            if (confirm.hasClass("process_checkout_disabled")){
                                confirm.removeClass("process_checkout_disabled")
                                confirm.addClass("process_checkout_enabled")
                            }
                        }
                    }
                }
            }

            function plus_onclick() {
                this.offsetParent.getElementsByTagName('a')[0].classList.remove('disabled')
                this.offsetParent.getElementsByTagName('a')[0].classList.add('js_add_cart_json')
            }

            for (i = 0; i < cart_qty.length; ++i) {
                if (cart_qty[i].value == 1) {
                    cart_minus[i].parentElement.setAttribute("class", "disabled")
                }
                cart_minus[i].parentElement.addEventListener("click", minus_onclick)
                cart_plus[i].parentElement.addEventListener("click", plus_onclick)
            }
        }
        }
        if (window.location.pathname == '/web/reset_password') {
            if (document.getElementsByClassName('sign-in')) {
                document.getElementsByClassName('sign-in')[0].innerHTML = "Request Password Reset"
            }
        }

        if (document.getElementById('next_port_select_id')) {
            document.getElementById('next_port_select_id').oninput = remove_border
            function remove_border(e) {
                setTimeout(function () {
                    if (document.getElementById('next_port_select_idautocomplete-list')) {
                        var nextport_autocomplete = document.getElementById('next_port_select_idautocomplete-list')
                        if (nextport_autocomplete.childElementCount < 1) {
                            $('#next_port_select_idautocomplete-list').css('border', 'white')
                        }
                    }
                }, 1);
            }
        }

        // Remove extra divider in mobile home menu
        if (document.getElementById('menu_part_mob_dropdown')){
            $('#menu_part_mob_dropdown>.dropdown-menu>li:last-child').remove()
        }
        if (document.getElementById('mobile_menu')){
            $('#mobile_menu .dropdown-menu>.divider').remove()
        }

        //check if user has logged in on page shop
        if (window.location.pathname.includes('/shop')) {
            openerp.jsonRpc('/customize_check_login').done(function (res) {
                // has not logged in
                if (res == true) {
                    document.getElementById("products_grid").id = "products_grid_before_login";
                }
            })
        }

        // prenvent user from submitting the signup form is checkbox is not ticked
        $(".oe_signup_form").submit(function (e) {
            if(!$("input[name='checkbox_agree_to']").is(":checked")) {
                e.preventDefault();
                var alert_msg = 'Please indicate that you accept the Terms & Conditions and Privacy Policy!'
                alert(alert_msg);
            }
        });
});

// window.onload = function() {
//     var categ_dropdown = sessionStorage.getItem("Categ_dropdown");
//     $('#dropdown_pub_cat').val(categ_dropdown);
//
//     var search_input = sessionStorage.getItem("Search_input");
//     $('#search_bar_input').val(search_input);
//
//     }
//     $('#dropdown_pub_cat').change(function() {
//         var categ_val = $(this).val();
//         sessionStorage.setItem("Categ_dropdown", categ_val);
//     });
//     $('#search_bar_input').change(function() {
//         var search_val = $(this).val();
//         sessionStorage.setItem("Search_input", search_val);
//     });



