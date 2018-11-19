function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    $(".form-login").submit(function(e){
        e.preventDefault();
        mobile = $("#mobile").val();
        passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        }
            //手机号正则
        var phoneReg=/(^1[3|4|5|7|8]\d{9}$)|(^09\d{8}$)/;
        //电话
        mobile=$.trim(mobile);
         if (!phoneReg.test(mobile)) {
             //手机号格式不正确
            $("#mobile-err span").html("请输入有效的手机号！");
            $("#mobile-err").show();
            return;
        }

        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        //前面的mobile 是后端定义的
        var data = {
            mobile:mobile,
            password:passwd
        };
        // $(this).serializeArray().map(function(x){data[x.name] = x.value;});
        var jsonData = JSON.stringify(data);  //这行必须要
        $.ajax({
            url:"/api/v1.0/sessions",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function (data) {
                if ("0" == data.errno) {
                    location.href = "/";  //返回首页
                    return;
                }
                else {
                    $("#password-err span").html(data.errmsg);
                    $("#password-err").show();
                    return;
                }
            }
        });
    });
})