function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}
$(document).ready(function() {
    if (getCookie("userobject") != "") {
        $.ajax({
            url: "/security/cookiechecker",
            method: "GET",
        }).done(function (msg) {
            msg = JSON.parse(msg);
            if (msg.valid) {
                if (!msg.defaultclass) {
                    $('#navigation').load('/static/includes/navbar_logged_noclass.html');
                }
                else {
                    $('#navigation').load('/static/includes/navbar_logged.html');
                }
            }
            else {
                $('#navigation').load('/static/includes/navbar_unlogged.html');
            }
            $('#footer').load('/static/includes/footer.html');
        }); 
    }
    else {
        $('#navigation').load('/static/includes/navbar_unlogged.html');
        $('#footer').load('/static/includes/footer.html');
    }
});