from django.conf.urls import url
from goods.views import IndexView,DetailView,ListView,CartCountView,SearchGoodsTypeView
urlpatterns = [
# 想要直接输入域名：http://127.0.0.1:8000就开始访问首页
# 一级域名goods什么也不写，一上来就匹配，二级域名index也什么都不配置
    # url(r'^test$', views.test, name="test")  # 用于测试
    url(r'^index$',IndexView.as_view(),name="index"), #首页
    url(r'^goods/(?P<goods_id>\d+)$',DetailView.as_view(),name="detail"), #商品详情页
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$',ListView.as_view(),name="list"), #商品列表详情页
    url(r'^search_cart$', CartCountView.as_view(), name="search_cart"),  # 搜索页购物车总条目的路由
    url(r'^search_goods_type$', SearchGoodsTypeView.as_view(), name="search_goods_type"),#搜索页所有商品分类的路由

]