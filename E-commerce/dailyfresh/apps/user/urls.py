from django.conf.urls import url
from user import views
# 下面是类视图导入的包  注册  激活   登录
from user.views import RegisterView,ActiveView,LoginView,LogoutView,Find_pwdView,Find_pwdView1,UserInfoView,UserOrderView,AddressView,DeleteAddrView,IsDefaultView,EditAddrView

# 登录装饰器包
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name="register"), #改版类视图配置路由，注册
    #这个token匹配得到是加密的一串符号，激活
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name="active"),#激活
    url(r'^login$', LoginView.as_view(), name="login"),#登录
    url(r'^logout$', LogoutView.as_view(), name="logout"),#退出登录

    url(r'^login/find$',Find_pwdView.as_view() , name="find"),#找回密码
    url(r'^login/find/reset$',Find_pwdView1.as_view() , name="reset"),#重置密码

    # url(r'^$',login_required(UserInfoView.as_view()), name="user"),  # 用户中心--个人信息
    # url(r'^order$', login_required(UserOrderView.as_view()), name="order"),  # 用户中心--全部订单
    # url(r'^address$',login_required(AddressView.as_view()), name="address"),  # 用户中心--收货地址

    url(r'^$', UserInfoView.as_view(), name="user"),  # 用户中心--个人信息
    url(r'^order/(?P<page>\d+)$', UserOrderView.as_view(), name="order"),  # 用户中心--全部订单
    url(r'^address$', AddressView.as_view(), name="address"),  # 用户中心--收货地址

    url(r'^address/delete(\d+)$', DeleteAddrView.as_view(), name="delete"),  #删除收货地址
    url(r'^address/default(\d+)$', IsDefaultView.as_view(), name="default"),#是否默认
    url(r'^address/edit(\d+)$', EditAddrView.as_view(), name="edit"),  #编辑


]