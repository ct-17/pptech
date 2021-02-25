(function() {
        'use strict';
        var website = openerp.website;
        website.openerp_website = {};
        $('input,textarea,select,label').filter('[required]:visible').each(function () {
            if (window.location.href.includes('/shop/confirm_order') || window.location.href.includes('/shop/checkout') || window.location.href.includes('/myaccounts') || window.location.href.includes('/web/signup') ) {
                let spanTag = document.createElement("span");
                spanTag.innerHTML = '<b>*</b>';
                this.parentNode.insertBefore(spanTag, this.nextSibling);
                spanTag.classList.add('ess_required');
                spanTag.style.cssText = "display: inline; position: absolute;";
            }
            else {
                let spanTag = document.createElement("span");
                spanTag.innerHTML = '<b>*</b>' + this.outerHTML;
                // this.parentNode.insertBefore(spanTag, this.nextSibling);
                spanTag.classList.add('ess_required');
                this.replaceWith(spanTag);
            }
        });
        if (window.location.pathname.includes('/shop/product/')) {
            if (document.getElementById("stock_level") === null){
                document.getElementById("product_descrpt").style.bottom="0px";
                var li = $("#product_description").find("li")
                for(var i=0;i<li.length;i++){
                   li[i].style.bottom="0px"
                }
            }
        }
        if($(".fa.fa-mobile")){
            try{
                $(".fa.fa-mobile")[0].style.display="none";
            }
            catch{
                
            }
        }

        $('#products_category_kanban').each( function () {
            // if ($('#js_search_bar').length){
            //     var t_search;
            //     t_search = document.createElement("t");
            //     t_search.setAttribute('t-call', 'website_sale.search')
            //
            //     var node = document.createTextNode("This is new.");
            //     t_search.appendChild(node);
            //     $('#js_search_bar')[0].appendChild(t_search)
            // };
            var img_index = 0;
            imgIndex_showing();
            function imgIndex_showing (){
                var i;
                var allimg = $('.mySlides');
                for (i=0; i< allimg.length; i++){
                    allimg[i].style.display = "none";
                }

                img_index ++;
                if (img_index > allimg.length){img_index=1}

                // allimg[img_index - 1].style.display = "block";

        };
        var loop =  setInterval(imgIndex_showing, 5000); // Change image every 2 seconds

    });
})();