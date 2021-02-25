$(document).ready(function() {
    if (window.location.pathname == '/web/signup' || window.location.pathname == '/web/login') {
        try{
            $('[id=top_menu]').css('display', 'none');
        }
        catch (e) {
        }
    }
})