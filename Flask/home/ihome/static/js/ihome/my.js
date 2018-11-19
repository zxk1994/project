function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function logout() {
      $.ajax({
            url:"/api/v1.0/sessions",
            type:"delete",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function (data) {
                if ("0" == data.errno) {
                    location.href = "/";  //返回首页
                }
            }
        });
}

$(document).ready(function(){
    $.get("/api/v1.0/user", function(data) {
        if ("4101" == data.errno) {
            location.href = "/login.html";
        }
        else if ("0" == data.errno) {
            $("#user-name").html(data.data.name);
            $("#user-mobile").html(data.data.mobile);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    }, "json");
})