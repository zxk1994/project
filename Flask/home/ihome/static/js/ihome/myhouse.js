$(document).ready(function(){
    //发布房源，只有认证后的才可以，先对用户进行实名认证
    $.get("/api/v1.0/users/auth", function(data){
        if ("4101" == data.errno) {
            location.href = "/login.html";
        } else if ("0" == data.errno) {
            if ("" == data.data.real_name || "" == data.data.id_card || null == data.data.real_name || null == data.data.id_card) {
                //未认证的用户，在页面显示去认证的按钮
                $(".auth-warn").show();
                return;
            }
            //已认证的用户，请求发布房源信息
            $.get("/api/v1.0/user/houses", function(result){
                if ("0"==result.errno){
                      $("#houses-list").html(template("houses-list-tmpl", {houses:result.data.houses}));
                }else{
                      $("#houses-list").html(template("houses-list-tmpl", {houses:[]}));
                }
            });
        }
    });
})