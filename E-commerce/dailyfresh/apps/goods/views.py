from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.core.cache import cache #导入页面数据缓存包
from goods.models import GoodsSKU, GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from order.models import OrderGoods  #在商品详情页会用到
from django_redis import get_redis_connection  #官网有方法导入redis包
from django.core.paginator import Paginator  #导入分页包

# 想要直接输入域名：http://127.0.0.1:8000就开始访问首页
# 一级域名goods什么也不写，一上来就匹配，二级域名index也什么都不配置
# http://127.0.0.1:8000
class IndexView(View):
    def get(self,request):
        """  首页"""
        # 一上来先尝试从缓存中获取数据,没有数据或时间过期，查询redis数据库
        context=cache.get("index_page_data")
        if context is None:
            print("缓存")
            #没有数据，查询数据库，有数据，不走数据库，使用缓存数据
            # 1、获取商品的种类信息
            types=GoodsType.objects.all()
            #2、获取首页轮播商品信息
            goods_banners=IndexGoodsBanner.objects.all().order_by("index")
            #3、获取首页促销活动信息
            promotion_banners=IndexPromotionBanner.objects.all().order_by("index")

            # 4、获取首页分类商品展示信息,（中间表链接）限制查询四个，用切片
            for type in types:
                # 获取type种类首页分类商品的图片展示信息
                image_banners=IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by("index")[0:4]
                #获取type种类首页分类商品的文字展示信息
                title_banners=IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by("index")[0:4]
                # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
                type.image_banners=image_banners
                type.title_banners=title_banners
            # 组织模板上下文
            context = {
                "types": types,
                "goods_banners": goods_banners,
                "promotion_banners": promotion_banners,
            }
            #设置缓存  key value 过期时间
            cache.set("index_page_data",context,3600)

        #5、获取用户购物车商品的数目
        #获取用户信息，如果登陆了，返回的是登录用户的对象
        user=request.user
        # 必须给cart_count一个初始变量，要不退出就报错了
        cart_count=0
        #判断用户有没有登录，登录的话链接redis数据库
        if user.is_authenticated():
            # 用户已经登录
            conn = get_redis_connection("default")  #链接redis数据库
            cart_key="cart_%d"%user.id
            cart_count=conn.hlen(cart_key)

        #更新数据库，购物车数据不存在添加，存在就修改
        context.update(cart_count=cart_count)

        # #组织模板上下文
        # context={
        #     "types":types,
        #     "goods_banners":goods_banners,
        #     "promotion_banners":promotion_banners,
        #     "cart_count":cart_count
        # }

        return render(request,"index.html",context)


# http://127.0.0.1:8000/goods/7  或者点击首页链接
class DetailView(View):
    """  商品详情页"""
    def get(self,request,goods_id):
        """  显示详情页"""
        try:
            sku=GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            #商品不存在
            return redirect(reverse("goods:index"))
        #获取商品的分类信息
        types=GoodsType.objects.all()
        #获取商品的评论信息
        sku_orders=OrderGoods.objects.filter(sku=sku).exclude(comment='')
        #获取商品信息,最新推荐
        new_skus=GoodsSKU.objects.filter(type=sku.type).order_by("-create_time")[0:2]

        #获取同一个SPU的其它规格商品
        same_spu_skus=GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)


        # 获取用户购物车商品的数目
        # 获取用户信息，如果登陆了，返回的是登录用户的对象
        user = request.user
        # 必须给cart_count一个初始变量，要不退出就报错了
        cart_count = 0
        # 判断用户有没有登录，登录的话链接redis数据库
        if user.is_authenticated():
            # 用户已经登录
            conn = get_redis_connection("default")  # 链接redis数据库
            cart_key = "cart_%d" % user.id
            cart_count = conn.hlen(cart_key)

            #添加用户的历史记录
            conn=get_redis_connection("default")
            history_key="history_%d" % user.id
            # 移除列表中的goods_id,防止重复点击显示相同内容，把第一次goods_id出现的删除
            conn.lrem(history_key, 0,goods_id)
            #把goods_id插入到列表的左侧
            conn.lpush(history_key,goods_id)
            #只保存用户最新浏览的5条数据
            conn.ltrim(history_key,0,4)

        #组织模板上下文,往里存数据
        context={
            "sku":sku,
            "types":types,
            "sku_orders":sku_orders,
            "new_skus":new_skus,
            "cart_count":cart_count,
            "same_spu_skus":same_spu_skus
        }
        #传给模板
        return render(request,"detail.html",context)


# 127.0.0.1:8000/list/3/2?sort=default
class ListView(View):
    """ 商品列表页 """
    #种类  页码 排序顺序
    #/list/种类id/页码？sort=排序方式
    def get(self,request,type_id,page):
        """  显示列表页"""
        #获取种类信息
        try:
            type=GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            #种类不存在
            return  redirect(reverse("goods:index"))

        #获取商品的分类信息,这个types必须和继承的模板那保持一致，因为detail都用的types
        types=GoodsType.objects.all()
        #获取排序的方式和商品的信息
        sort =request.GET.get("sort")
        if sort=="price":
            skus=GoodsSKU.objects.filter(type=type).order_by("price")
        elif sort=="hot":
            skus=GoodsSKU.objects.filter(type=type).order_by("-sales") #根据销量
        else:
            sort="default" #一开始什么也没操作，给个默认值
            skus = GoodsSKU.objects.filter(type=type).order_by("-id")

        #对数据进行分页,2 代表每页只有2个数据显示
        paginator = Paginator(skus,1)
        #获取第page页的内容
        try:
            page=int(page) #先转化成整型
        except Exception as e:
            page=1   #有异常回到第一页
        if page > paginator.num_pages:   #如果输入的大于分的总页数，返回第一页
            page =1
        #获取第page页的page实例对象
        skus_page=paginator.page(page)

        # todo 进行页码的控制，列表上最多显示5个列表
        # paginator.num_pages  总页数
        #1、总页数小于5页，页面上显示所有页码
        #2、如果当前页是前3页，显示1-5页
        #3、如果当前页是后3页，显示后5页
        #4、其它情况，显示当前页的前2页、当前页、当前页的后2页
        num_pages=paginator.num_pages
        if num_pages <5:
            pages=range(1,num_pages + 1)
        elif page <=3:
            pages=range(1,6)
        elif num_pages - page <=2:
            pages=range(num_pages -4 ,num_pages +1)
        else:
            pages=range(page-2,page+3)


        #获取新品信息
        new_skus=GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取用户购物车商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            conn = get_redis_connection("default")  # 链接redis数据库
            cart_key = "cart_%d" % user.id
            cart_count = conn.hlen(cart_key)

        #组织模板上下文,注意千万别加空格，注意传参对
        context={
            "type":type,
            "types":types,
            "skus_page":skus_page,
            "new_skus":new_skus,
            "cart_count":cart_count,
            "sort":sort,  #传参为了比较，增加样式
            "pages":pages
        }
        return render(request,"list.html",context)

# http://127.0.0.1:8000/search/?q=苹果
class CartCountView(View):
    """  获取搜索页的右上角购物车总条目数"""
    def get(self,request):
        """  获取购物车总条目数"""
        user=request.user  #获取redis数据库
        cart_count=0
        #判断用户有没有登录
        if user.is_authenticated():
            #用户已经登录
            conn = get_redis_connection("default")  #连接redis数据库
            #首页购物车商品总条目的显示功能，打算使用redis内存式数据
            cart_key="cart_%d" % user.id
            cart_count = conn.hlen(cart_key)
            from django.http import  JsonResponse
            res=JsonResponse ({"code":"100001","msg":"ok","data":cart_count},content_type="application/json")
            # 跨域的问题：
            res["Access-Control-Allow-Origin"] ="*"
            res["Access-Control-Allow-Methods"]="POST,GET,OPTIONS"
            return res
        else:
            #用户未登录
            from django.http import JsonResponse
            res= JsonResponse({"code": "100000", "msg": "error", "data": cart_count}, content_type="application/json")
            res["Access-Control-Allow-Origin"] = "*"
            res["Access-Control-Allow-Methods"] = "POST,GET,OPTIONS"
            return res

class SearchGoodsTypeView(View):
    """  获取所有商品分类"""
    def get(self,request):
        """ 获取所有商品分类"""
        types=GoodsType.objects.all()
        json_list =[]
        for type in types:
            json_dict ={}
            json_dict['id']=type.id
            json_dict['name']=type.name
            json_dict['logo']=type.logo
            json_list.append(json_dict)
        from django.http import HttpResponse
        import json
        return HttpResponse(json.dumps(json_list),content_type="application/json")





# def test(request):
#     """  用于测试"""
#     goodstype=GoodsType.objects.get(id=3)
#     return render(request,"test.html",{"goodstype":goodstype})
