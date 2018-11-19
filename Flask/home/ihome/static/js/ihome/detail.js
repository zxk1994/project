function hrefBack() {
    history.go(-1);
}

function decodeQuery(){
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function(result, item){
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

$(document).ready(function(){
    //获取详情页面要展示的房屋编号
    var house_id = decodeQuery()["id"];
    $.get("/api/v1.0/houses/"+ house_id, function (data) {
        if ("0" == data.errno) {
            console.log(data)
            $(".swiper-container").html(template("house-image-tmpl", {"img_urls":data.data.house.img_urls, "price":data.data.house.price}));
            $(".detail-con").html(template("house-detail-tmpl", {"house":data.data.house}));
            var mySwiper = new Swiper ('.swiper-container', {
                loop: true,
                autoplay: 2000,
                autoplayDisableOnInteraction: false,
                pagination: '.swiper-pagination',
                paginationType: 'fraction'
            })
            // data.user_id为访问页面用户,data.data.user_id为房东
            if (data.data.user_id != data.data.house.user_id) {
                $(".book-house").attr("href", "/booking.html?hid="+data.data.house.hid);//可以跳转到预订界面
                $(".book-house").show();
            }
        }
    }, "json")
})