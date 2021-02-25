$(document).ready(function () {
     if (document.getElementsByClassName("js_quantity form-control").add_qty) {
         var cart_qty = document.getElementsByClassName("js_quantity form-control").add_qty
         cart_qty.onkeypress = function(e) {
            e = e || window.event;
            var charCode = (typeof e.which == "undefined") ? e.keyCode : e.which;
            var charStr = String.fromCharCode(charCode);
            if (/\D/.test(charStr)) {
                return false;
            }
        };
         cart_qty.type = 'number';
         cart_qty.addEventListener("change", product_detail_cart_qty_onchange);
     }
     // if (document.getElementById('cart_instance')){
     //     if (document.getElementsByClassName("js_quantity form-control")){
     //         var cart_line = document.getElementsByClassName("js_quantity form-control")
     //         for (var i=0; i<cart_line.length;i++){
     //             cart_line[i].type = 'number';
     //             cart_line[i].addEventListener("change", cart_page_cart_qty_onchange);
     //         }
     //     }
     // }
     // if (document.getElementById('process_checkout')){
     //     document.getElementById('process_checkout').style.display = "none";
     // }
     // if (document.getElementById('confirm_process_checkout')){
     //     document.getElementById('confirm_process_checkout').addEventListener('click',function(){
     //     document.getElementById('confirm_process_checkout').style.display = "none";
     //     setTimeout(function(){document.getElementById('process_checkout').style.display = "block";}, 1500);
     //     });
     // }
 });

function product_detail_cart_qty_onchange(){
    if (document.getElementsByClassName("js_quantity form-control").add_qty.value < 1){
        alert('Your ADD TO CART quantity is less than minimum order limit. Please make sure the quantity is at least 1.')
        document.getElementsByClassName("js_quantity form-control").add_qty.value = 1
     }
    else{
         $(".oe_cart input.js_quantity").trigger("change");
    }
}

function cart_page_cart_qty_onchange(){
    if (this.value < 1){
        alert('Your ADD TO CART quantity is less than minimum order limit. Please make sure the quantity is at least 1.')
        this.value = 1
     }
    else{
        $(".oe_cart input.js_quantity").trigger("change");
    }
}

