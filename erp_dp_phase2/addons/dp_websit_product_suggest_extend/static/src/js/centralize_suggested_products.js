$(document).ready(function () {
    if (document.getElementsByClassName("col-12 col-sm-6 col-sm-2dot4 col-md-2dot4 col-lg-2dot4")) {
        var suggest_products = document.getElementsByClassName("col-12 col-sm-6 col-sm-2dot4 col-md-2dot4 col-lg-2dot4")
        var length = suggest_products.length
        var percentage = 50 - (length-1) * 12.5
        if (length !== 5){
            for(var i=0;i<length;i++){
                suggest_products[i].style.transform = "translateX(-" + percentage + "%)"
                suggest_products[i].style.left = percentage + "%"
            }
        }
    }
});

