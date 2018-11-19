function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    //一开始就要获取信息的
    $.get("/api/v1.0/users/auth", function(data){
        if ("4101" == data.errno) {
            location.href = "/login.html";
        }
        else if ("0" == data.errno) {
            if (data.data.real_name && data.data.id_card) {
                $("#real-name").val(data.data.real_name);
                $("#id-card").val(data.data.id_card);
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                $("#form-auth>input[type=submit]").hide();
            }
        }
    }, "json");
    //设置信息的
    $("#form-auth").submit(function(e){
        e.preventDefault();
        var realName=$("#real-name").val();
        var idCard=$("#id-card").val();
        if ($("#real-name").val()=="" || $("#id-card").val() == "") {
            $(".error-msg").show();
        }
        //real_name代表后台get("real_name")
        var data = {
            real_name:realName,
            id_card:idCard
        };

        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/users/auth",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function (data) {
                if ("0" == data.errno) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true); //添加属性  禁用
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();  //保存按钮隐藏
                }
            }
        });
    })

})

