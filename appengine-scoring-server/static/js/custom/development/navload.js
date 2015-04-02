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
            method: "POST",
            data: {
                cookie: getCookie("userobject")
            }
        }).done(function (msg) {
            if (msg == "True") {
                $('#navigation').load('/static/includes/navbar_unlogged.html');
            }
            else {
                $('#navigation').load('/static/includes/navbar_logged.html');
            }
            $('#footer').load('/static/includes/footer.html');
        }); 
    }
    else {
        $('#navigation').load('/static/includes/navbar_unlogged.html');
        $('#footer').load('/static/includes/footer.html');
    }
});