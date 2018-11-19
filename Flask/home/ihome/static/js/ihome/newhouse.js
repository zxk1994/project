function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    $.get("/api/v1.0/areas", function (data) {
        if ("0" == data.errno) {
            var areas=data.data;  //存储的结果格式15组 data{data{}}
            // for (var i=0; i<areas.length; i++) {
            //     var area=areas[i]
            //     $("#area-id").append('<option value="'+area.aid+'">'+area.aname+'</option>');
            // }
            //使用js插件模板
             html = template("area-tmpl", {areas: areas});
            $("#area-id").html(html);
        }else{
            alert(data.errmsg)
        }
    }, "json")

    $("#form-house-info").submit(function(e){
        e.preventDefault();
        var formData = $(this).serializeArray(); //得到表单中所有的数据，返回值[{} {} {}]
        for (var i=0; i<formData.length; i++) { //遍历循环得到每一个{}
            if (!formData[i].value) {
                $(".error-msg").show();
                return;
            }
        }
        var data = {};
        $(this).serializeArray().map(function(x){
            data[x.name] = x.value;
        }); //map循环填充到data里

        var facility = []; // 用来保存勾选了的设施编号
        // 通过jquery筛选出勾选了的页面元素
        // 通过each方法遍历元素
        $("input:checkbox:checked[name=facility]").each(function(i){facility[i] = this.value;});
        data.facility = facility;
        //得到这个格式的{"title":"房屋1","price":"200", "facility":[1,3,5]}
        var jsonData = JSON.stringify(data);  //转化为json字符串
        $.ajax({
            url:"/api/v1.0/houses/info",
            type:"POST",
            data: jsonData,
            contentType: "application/json",
            dataType: "json",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function (data) {
                if ("4101" == data.errno) {
                    location.href = "/login.html";
                } else if ("0" == data.errno) {
                    $("#house-id").val(data.data.house_id);
                    $(".error-msg").hide();
                    $("#form-house-info").hide();
                    $("#form-house-image").show();
                }else{
                    alert(data.errmsg)
                }
            }
        });
    })
    $("#form-house-image").submit(function(e){
        e.preventDefault();
        $('.popup_con').fadeIn('fast');
        var options = {
            url:"/api/v1.0/houses/image",
            type:"POST",
            headers:{
                "X-CSRFTOKEN":getCookie("csrf_token"),
            },
            success: function(data){
                if ("4101" == data.errno) {
                    location.href = "/login.html";
                } else if ("0" == data.errno) {
                    $(".house-image-cons").append('<img src="'+ data.data.image_url+'">');
                    $('.popup_con').fadeOut('fast');
                }else{
                    alert(data.errmsg)
                }
            }
        };
        $(this).ajaxSubmit(options);
    });
})