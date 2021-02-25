$(document).ready(function () {
    if (document.getElementsByClassName("shopping-cart-json-rpc")) {
        $('.shopping-cart-json-rpc').each(function (index) {
            $(this).on("click", function () {
                openerp.jsonRpc('/shop/custom_cart_update_json', 'call', {
                        'product_id': this.previousElementSibling.value
                }).done(function(data) {
                    return_data = JSON.parse(data);
                    $(document.getElementById('hide_shopping_cart')).removeClass();
                    document.getElementById('shopping_cart_value').innerHTML = return_data.return_sum;
                    $(document.getElementsByClassName('col-md-2 text-right')[0]).fadeOut(10).fadeIn(400);
                });
            });
        });
    }
    $('#typedate').datepicker({
        dateFormat: "dd/mm/yy",

    })


});