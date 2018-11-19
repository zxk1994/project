from django.shortcuts import render,redirect   #重定向
from django.core.urlresolvers import reverse   #使用反向解析,导入包
from django.views.generic import View  #使用类视图导入View包
# 下面这两个导入的是激活邮件加密的包
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# 下面两个在激活类中用到了
from django.http import HttpResponse
from itsdangerous import SignatureExpired
from user.models import User,Address
# 下面这个包在发送邮件用到了
from django.core.mail import send_mail
from celery_tasks.tasks import send_register_active_email
# 登录用户认证包
from django.contrib.auth import authenticate,login,logout
import re
# 登录装饰器包
from utils.mixin import LoginRequiredMixin
# 导入历史浏览记录
from goods.models import GoodsSKU
#下面是UserOrderView订单页包
from django_redis import get_redis_connection
from order.models import OrderInfo,OrderGoods
from django.core.paginator import Paginator



#/user/register   直接写域名 GET方式  提交注册是POST方式  api方法
# 想要优化，用同一个路由/user/register，区分GET  和POST方法
# def register(request):
#     """  注册"""
#     if request.method=="GET":
#         # 显示注册页面
#         return render(request,"register.html")
#     elif request.method=="POST" :
#         """进行注册处理"""
#         # 接收数据
#         username = request.POST.get("user_name")
#         passsword = request.POST.get("pwd")
#         email = request.POST.get("email")
#         cpwd = request.POST.get("cpwd")
#         allow = request.POST.get("allow")
#
#         # 进行数据校验
#         if not all([username, passsword, email]):
#             # 数据不完整
#             return render(request, "register.html", {"errmsg": "数据不完整"})
#
#         # 检验用户名是否重复
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             # 用户名不存在
#             user = None
#         if user:
#             # 用户名存在
#             return render(request, "register.html", {"errmsg": "用户名已存在"})
#
#         # 校验邮箱
#         if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
#             return render(request, "register.html", {"errmsg": "邮箱格式不正确"})
#
#         # 校验两次密码
#         if (passsword != cpwd):
#             return render(request, "register.html", {"errmsg": "密码不匹配"})
#
#         # 校验是否点击了协议
#         if allow != "on":
#             return render(request, "register.html", {"errmsg": "请同意协议"})
#
#         # 进行业务处理，进行用户注册 (得到的密码加密)--往数据库加数据 user得到的是用户名
#         user = User.objects.create_user(username, email, passsword)
#         # 不想让其默认情况下激活，就is_active=0     为1就是激活
#         user.is_active = 0
#         user.save()
#         # 返回应答
#         return redirect(reverse("goods:index"))  # 反向解析使用名字：名字


# def register_handle(request):

# 使用类视图改版的
class RegisterView(View):
    """  注册"""
    def get(self,request):
        if request.method=="GET":
            # 显示注册页面
            return render(request, "register.html")

    def post(self,request):
        """进行注册处理"""
        # 接收数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        cpwd = request.POST.get("cpwd")
        allow = request.POST.get("allow")

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, "register.html", {"errmsg": "数据不完整"})
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})
        # 校验两次密码
        if (password != cpwd):
            return render(request, "register.html", {"errmsg": "密码不正确"})
        # 校验是否点击了协议
        if allow != "on":
            return render(request, "register.html", {"errmsg": "请同意协议"})

        # 检验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名存在
            return render(request, "register.html", {"errmsg": "用户名已存在"})

        # 进行业务处理，进行用户注册
        # 进行业务处理，进行用户注册 (得到的密码加密)--往数据库加数据 user得到的是用户名
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接，http://127.0.0.1:8000/user/active/3   这个3是对应的用户需要加密

        # 加密用户身份信息，生成激活tokon
        serializer=Serializer(settings.SECRET_KEY,3600)#创建加密对象，并设置过期信息
        info={"confirm":user.id}  #定义加密的字符串
        token=serializer.dumps(info)#获取加密后的字符串信息  得到的是个b字节的，需要解码
        token=token.decode()  #注意解码，链接就不会出现b字节了

        # #开始真正的发邮件
        # subject="天天生鲜欢迎你使用"
        # # message  发送邮件的内容
        # message=""  #这个不能删掉，默认是第二个参数
        # # 下面的这个就可以解析前端代码了
        # html_message="<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面的链接激活您的账户<br>" \
        #              "<a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>"\
        #              %(username,token,token)
        #
        # sender=settings.EMAIL_FROM  #获取settings里的发送者信息
        # receiver=[email,"1761299425@qq.com"]   #此处是个列表，填写对方的邮箱，这里的email是获取的文本框的值，可给多人发送
        # # 最后的html_message=html_message，前面的那个底层代码html_message=，缺省参数放在最后，后面那个是传递的值
        # # 查看send_mail底层代码  ctrl+鼠标左击
        # send_mail(subject,message,sender,receiver,html_message=html_message)  #发送邮件的方式，整合
        # 发邮件调用方法

        send_register_active_email.delay(email,username,token)

        # 返回应答
        return redirect(reverse("goods:index"))  # 反向解析使用名字：名字


class ActiveView(View):
    """  用户激活"""
    # 这个token得到路由那 active/后匹配的一系列加密字符，开始解密
    def get(self,request,token):
        """ 进行用户激活"""
        #进行解密，获取需要解密的用户信息
        serializer =Serializer(settings.SECRET_KEY,3600)
        try:
            #loads 解密   dumps  加密
            info=serializer.loads(token)
            # 获取待激活用户的id 字典的键，可得到值
            user_id=info["confirm"]
            # user_name = info["confirm"]
            #根据id获取用户信息
            user = User.objects.get(id=user_id)
            # user = User.objects.get(username=user_name)
            user.is_active = 1
            user.save()
            # 跳转到登录页面
            return redirect(reverse("user:login"))
        except SignatureExpired as e:
            return HttpResponse("激活链接已过期")


class LoginView(View):
    """  登录"""
    def get(self,request):
        """  显示登录页面"""
        #判断是否记住了用户名 如果username在后台cookie里，得到cookie里的username
        if "username" in request.COOKIES:
            username=request.COOKIES.get("username")
            # checked默认被选中
            checked="checked"
        else:
            username= ""
            checked= ""
        return render(request,"login.html",{"username":username, "checked":checked})
    def post(self,request):
        """  登录校验"""
        #1、接收数据
        username=request.POST.get("username")
        password=request.POST.get("pwd")
        #2、校验数据
        if not all([username,password]):
            return render(request,"login.html",{"errmsg":"数据不完整"})
        #业务处理 登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
           #用户名密码正确
            if user.is_active:
                #用户已激活
                #记录用户的登录状态,固定写法，就不会每次打开一个页面，都登陆一次了
                login(request,user)

                # 获取登录后要跳转到的地址，第二个参数是默认，如果第一个不满足，执行第二个
                next_url=request.GET.get("next",reverse("goods:index"))
                response= redirect(next_url)#登录成功后，还跳转到来的界面

                #判断是否需要记住用户名
                remember = request.POST.get("remember")
                if remember =="on":
                    #点击了，记住了用户名，设置cookie过期时间7天，需3个参数第一个键，第二个值，过期时间
                    response.set_cookie("username",username,max_age=7*24*3600)
                else:
                    response.delete_cookie("username")#删除cookie
                #返回首页
                return response
            else:
                #用户未激活
                return render(request,"login.html",{"errmsg":"账户未激活"})
        else:
           #用户名或密码错误
           return render(request, "login.html", {"errmsg": "用户名或密码错误"})

class LogoutView(View):
    """  退出登录"""
    def get(self,request):
        # 清除用户的session信息,清除会话机制，官方
        logout(request)
        # 跳转到首页
        return redirect(reverse("goods:index"))


# 重置密码部分
class Find_pwdView(View):
    def get(self,request):
        return render(request, "find_pwd1.html")

    def post(self,request):
       pwd1= request.POST.get("pwd1")
       pwd2=request.POST.get("pwd2")
       if pwd1 != pwd2:
           return render(request, "find_pwd2.html", {"errmsg": "密码不正确"})
       else:
            User.objects.create_user(pwd1,pwd2)
       # return redirect(reverse("user:login"))
       # user = authenticate(username=pwd1, password=pwd2)
       # if user is not None:
            return render(request, "login.html")

class Find_pwdView1(View):
    def get(self,request):
       pass

    def post(self, request):

        username = request.POST.get("username")
        email = request.POST.get("email")

        user = User.objects.create_user(username, email)
        user.is_active = 0
        user.save()
        # 加密用户身份信息，生成激活tokon
        serializer = Serializer(settings.SECRET_KEY, 3600)  # 创建加密对象，并设置过期信息
        info = {"confirm": user.id}  # 定义加密的字符串
        token = serializer.dumps(info)  # 获取加密后的字符串信息  得到的是个b字节的，需要解码
        token = token.decode()  # 注意解码，链接就不会出现b字节了
        # 发送邮件
        send_register_active_email.delay(email, username, token)
        return render(request, "find_pwd2.html")

# 修改选中后的超连接样式：传参形式
#http://127.0.0.1:8000/user
class UserInfoView(LoginRequiredMixin, View):
    """  用户中心--个人信息"""
    def get(self,request):
        """   显示页面"""
        user=request.user
        try:
            addr=Address.objects.get(user=user,is_default=True)
        except Exception as e:
            addr=None

        # 个人信息下面历史浏览记录部分，获取历史浏览记录，传给前端
        conn=get_redis_connection("default")
        history_key="history_%d" %user.id
        #获取用户最新浏览的5个信息,得到是商品的id
        sku_ids=conn.lrange(history_key,0,4)
        # 从数据库查询具体的商品信息
        goods_li=GoodsSKU.objects.filter(id__in=sku_ids)

        #遍历获取用户浏览的商品信息
        goods_li=[]
        for id in sku_ids:
            goods=GoodsSKU.objects.get(id=id)
            goods_li.append(goods)
        #组织上下文关系
        context={
            "page": "user",
            "addr": addr,
            "goods_li":goods_li
        }
        return render(request,"user_center_info.html",context)




#http://127.0.0.1:8000/user/order
class UserOrderView(LoginRequiredMixin, View):
    """  用户中心--订单页"""
    def get(self,request,page):
        """   显示页面"""
        #获取用户的订单信息
        user=request.user
        orders=OrderInfo.objects.filter(user=user).order_by('-create_time')
        #遍历获取订单商品的信息
        for order in orders:
            #根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)
            #遍历order_skus 计算商品的小计
            for order_sku in order_skus:
                #计算小计
                amount = order_sku.count * order_sku.price
                #动态给order_sku 增加属性 amount 保存订单商品的信息
                order_sku.amount = amount

            #动态给order增加属性，保存订单状态标题,前端可以直接用
            order.status_name=OrderInfo.ORDER_STATUS[order.order_status]

            #动态给order增加属性，保存订单商品的信息
            order.order_skus=order_skus

        #分页
        paginator=Paginator(orders,1)  #1代表每页显示的数量
        #获取第page页的内容
        try:
            page=int(page)
        except Exception as e:
            page=1
        if page > paginator.num_pages:
            page = 1
        #获取第page页的Page实例对象
        order_page=paginator.page(page)

        # todo 进行页码的控制，列表上最多显示5个列表
        # paginator.num_pages  总页数
        # 1、总页数小于5页，页面上显示所有页码
        # 2、如果当前页是前3页，显示1-5页
        # 3、如果当前页是后3页，显示后5页
        # 4、其它情况，显示当前页的前2页、当前页、当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)
        #组织上下文
        context={
            "order_page":order_page,
            "pages":pages,
            "page":"order"   #传递参数用的{"page":"order"}
        }
        return render(request,"user_center_order.html",context)


#http://127.0.0.1:8000/user/address
class AddressView(LoginRequiredMixin, View):
    """  用户中心--收货地址"""
    def get(self,request):
        """   显示页面"""
        # 一进来地址页的时候需要进行判断：
        user=request.user  #得到现在登录的用户信息
        # 获取用户的默认收获地址，这个address得到是个对象，查询到的整条数据
        try:
            # address = Address.objects.get(user=user, is_default=True)
            address = Address.objects.filter()
        except Exception as e:
            # 不存在默认地址，给个None
            address = None
        return render(request,"user_center_site.html",{"page":"address","address":address})

    def post(self,request):
        """  添加地址  """
        #1、获得数据
        receiver = request.POST.get("receiver")
        addr=request.POST.get("addr")
        zip_code=request.POST.get("zip_code")
        phone=request.POST.get("phone")
        #2、校验数据
        if not all([receiver,addr,phone]):
            return render(request,"user_center_site.html",{"errmsg":"数据不完整"})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
            return render(request, "user_center_site.html", {"errmsg": "手机格式不正确"})
        #3、业务处理--往数据库写东西
        # 如果用户是否存在默认地址，添加的地址不作为默认地址，否则作为默认地址
        # 先查询数据库判断
        #获取登录用户对应的user对象
        user=request.user
        try:
            address=Address.objects.get(user=user,is_default=True)
            # address = Address.objects.filter()
        except Exception as e:
            #不存在默认地址，给个None
            address=None
        if address:
            # 如果地址存在，为真，不默认地址
            is_default=False
        else:
            is_default=True

        #判断完，开始真正的向数据库添加数据了,必须写user

        Address.objects.create(user=user,receiver=receiver,addr=addr,zip_code=zip_code,phone=phone,is_default=is_default)

        #返回应答
        return redirect(reverse("user:address"))
        # return render(request, "user_center_site.html")

class DeleteAddrView(View):
    """  删除收货地址"""
    def get(self,request,bid):
        addr=Address.objects.get(id=bid)
        addr.delete()
        return redirect(reverse("user:address"))

class IsDefaultView(View):
    """  是否默认 """
    def get(self,request,bid):
        # 收货地址默认
        user = request.user
        # try:
        addr = Address.objects.get(id=bid)
        addr1 = Address.objects.get(user=user, is_default=True)
        addr1.is_default = False
        addr.is_default = True
        addr1.save()
        addr.save()
        # except Exception as e:
            # 不存在默认地址，给个None
            # addr=None
            # addr1=None
        return redirect(reverse("user:address"))
        # return redirect(reverse("user:address"))
        # return render(request, "user_center_site.html",{"checked":checked})

class EditAddrView(View):
    """  编辑收货地址 """
    def get(self,request ,bid1):
        addr = Address.objects.get(id=bid1)
        edit_receiver = addr.receiver
        edit_addr = addr.addr
        edit_zip_code = addr.zip_code
        edit_phone = addr.phone
        return render(request, "user_center_site.html",{"edit_receiver": edit_receiver,"edit_addr":edit_addr,"edit_zip_code":edit_zip_code,"edit_phone":edit_phone})
    def post(self,request,bid1):
        # 1、获得数据
        user = request.user
        receiver = request.POST.get("receiver")
        addr = request.POST.get("addr")
        zip_code = request.POST.get("zip_code")
        phone = request.POST.get("phone")
        # 2、校验数据
        if not all([receiver, addr, phone]):
            return render(request, "user_center_site.html", {"errmsg": "数据不完整"})
        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, "user_center_site.html", {"errmsg": "手机格式不正确"})
        #3、跟新数据库
        new_addr=Address.objects.get(user=user,id=bid1)
        new_addr.receiver=receiver
        new_addr.addr=addr
        new_addr.zip_code=zip_code
        new_addr.phone=phone
        new_addr.save()
        return redirect(reverse("user:address"))
        # new_receiver=receiver
        # new_addr=addr
        # new_zip_code=zip_code
        # new_phone=phone
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        #     # address = Address.objects.filter()
        # except Exception as e:
        #     # 不存在默认地址，给个None
        #     address = None
        # if address:
        #     # 如果地址存在，为真，不默认地址
        #     is_default = False
        # else:
        #     is_default = True
        # Address.objects.create(user=user, receiver=new_receiver, addr=new_addr, zip_code=new_zip_code, phone=new_phone,is_default=is_default)
        # return redirect(reverse("user:address"))