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

$(document).ready(function () {
    //一开始就获取用户资料
    $.get("/api/v1.0/user", function(data){
        if ("4101" == data.errno) {
            location.href = "/login.html";
        }
        else if ("0" == data.errno) {
            $("#user-name").val(data.data.name);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    })
    $("#form-avatar").submit(function (e) {
        // 组织浏览器对于表单的默认行为
        e.preventDefault();
        $('.image_uploading').fadeIn('fast');
        var options = {
            url: "/api/v1.0/users/avatar",
            method: "post",
            dataType: "json",
            headers: {
                "X-CSRFTOKEN": getCookie("csrf_token")
            },
            success: function (data) {
                if ("0" == data.errno) {
                    $('.image_uploading').fadeOut('fast');
                    $("#user-avatar").attr("src", data.data.avatar_url)//写返回的图片路径
                } else {
                   alert(data.errmsg)
                }
            }
        };
        $(this).ajaxSubmit(options); //异步的进行ajax。
    })
    $("#form-name").submit(function(e){
        e.preventDefault();
        //获取值，必须转化成字典形式，json
        data=$("#user-name").val()
        if(!data){
            alert("请输入用户名！");
            return;
        }

        //拿到的是req_data.get("name") 执行的
        data={
            "name":data
        };

        var jsonData = JSON.stringify(data);
        $.ajax({
            url:"/api/v1.0/users/name",
            type:"PUT",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function (data) {
                if ("0" == data.errno) {
                    $(".error-msg").hide();
                    showSuccessMsg(); // 展示保存成功的页面效果
                } else if ("4001" == data.errno) {
                    $(".error-msg").show();
                } else if ("4101" == data.errno) { // 4101代表用户未登录，强制跳转到登录页面
                    location.href = "/login.html";
                }
            }
        });
    })
})

