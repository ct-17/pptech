$(document).ready(function() {
    if (window.location.pathname == '/web/signup' || window.location.pathname == '/web/login') {
        try{
            $('[id=top_menu]').css('display', 'none');
        }
        catch (e) {
        }
    }
})

function showPassword(obj, el) {
    var obj = document.getElementById('password');
    if (obj.type === "password") {
        obj.type = "text";
        el.className = 'fa fa-eye-slash password field-icon';
    } else {
        obj.type = "password";
        el.className = 'fa fa-eye password field-icon';
    }
}

function showPasswordReset(obj, el) {
    var obj = document.getElementById('password');
    if (obj.type === "password") {
        obj.type = "text";
        el.className = 'fa fa-eye-slash password field-icon';
    } else {
        obj.type = "password";
        el.className = 'fa fa-eye password field-icon';
    }
}

function showPasswordResetConfirm(obj, el) {
    var obj = document.getElementById('confirm_password');
    if (obj.type === "password") {
        obj.type = "text";
        el.className = 'fa fa-eye-slash confirm_password field-icon';
    } else {
        obj.type = "password";
        el.className = 'fa fa-eye confirm_password field-icon';
    }
}