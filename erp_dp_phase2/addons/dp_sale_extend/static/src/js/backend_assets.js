
    // for document.getElementsByClassName('oe_view_manager_switch oe_button_group oe_right')
    // [0].lastElementChild.lastElementChild.getAttribute('data-original-title')

$(document).ready(function () {
    if (document.getElementsByClassName('oe_view_manager_switch oe_button_group oe_right')) {
        var header_view = document.getElementsByClassName('oe_view_manager_switch oe_button_group oe_right')
        var length = header_view.length
        for(var i=0;i<length;i++){
            if (header_view[i].lastElementChild.lastElementChild.getAttribute('data-original-title') === 'Form view') {
                header_view[i].lastElementChild.classList.add("you_shall_not_show")
            }
        }
    }
});
