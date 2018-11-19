from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from goods.models import GoodsSKU
from user.models import Address
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin
from django.http import JsonResponse
from order.models import OrderInfo,OrderGoods
from datetime import  datetime
from django.db import transaction  #添加事务
from alipay import AliPay   #导入


# http://127.0.0.1:8000/cart/ 点击结算变成
# http://127.0.0.1:8000/order/place
class OrderPlaceView(LoginRequiredMixin,View):
    """  提交订单显示页面"""
    def post(self,request):
        """  提交订单显示页面"""
        #获取登录的用户
        user=request.user
        #获取参数sku_ids
        sku_ids = request.POST.getlist('sku_ids')   #[1,2,7]以列表的形式显示
        #校验参数
        if not sku_ids:
            #跳转到购物车界面
            return redirect(reverse("cart:show"))
        conn = get_redis_connection('default')
        cart_key = "cart_%d" % user.id

        skus=[]
        #保存商品的总件数和总价格
        total_count = 0
        total_price =0
        #遍历sku_ids 获取用户要购买的商品的信息
        for sku_id in sku_ids:
            #根据商品的id 获取商品的数量
            sku=GoodsSKU.objects.get(id=sku_id)
            #获取用户所要购买的商品的数量
            count=conn.hget(cart_key,sku_id)
            #计算商品的小计
            amount = sku.price * int(count)
            #动态给sku增加属性count 保存购买商品的数量
            sku.count = count
            # 动态给sku增加属性amount 保存购买商品的小计
            sku.amount = amount
            #增加
            skus.append(sku)
            #累加计算商品的总件数和总价格
            total_count += int(count)
            total_price += amount

        #运费：实际开发的时候，属性一个子系统
        transit_price = 10  #写死的内容
        #实付款
        total_pay = total_price + transit_price

        #获取用户的收件地址
        addrs = Address.objects.filter(user=user)

        #组织上下文  列表转化成字符串
        sku_ids=','.join(sku_ids) #[1,2,7] --1,2,7
        context={
            "skus": skus,
            "total_count":total_count,
            "total_price":total_price,
            "transit_price": transit_price,
            "total_pay":total_pay,
            "addrs":addrs,
            "sku_ids":sku_ids
        }
        #使用模板
        return render(request,"place_order.html",context)

#前端传递的参数，地址id(addr_id) 支付方式（pay_method）用户要购买的商品id 字符串（sku_ids）
# http://127.0.0.1:8000/cart/ 点击结算变成
# http://127.0.0.1:8000/order/place
#点击提交订单
class OrderCommitView1(View):
    """  订单创建 运用了悲观锁"""
    #添加事务，这样的话就会要么都成功，要么都失效。
    @transaction.atomic
    def post(self,request):
        """  订单创建 """
        #判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({"res": 0, "errmsg": "请先登录"})
        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get("pay_method")
        sku_ids=request.POST.get("sku_ids")  #在前端模板提交订单那（）
        # 数据校验
        if not all([addr_id,pay_method,sku_ids]):
            return JsonResponse({"res": 1, "errmsg": "数据不完整"})
        #校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({"res": 2, "errmsg": "非法的支付方式"})
        #校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            #地址不存在
            return JsonResponse({"res": 3, "errmsg": "地址非法"})
        #todo : 创建订单核心业务
        #组织参数
        #订单id : 20171122181630 + 用户id    时间戳
        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+ str(user.id)

        #运费
        transit_price = 10
        #总数目和总金额
        total_count = 0
        total_price = 0

        #设置事务的保存点
        save_id = transaction.savepoint()
        try:
            #todo: 向df_order_info 表中添加一条记录
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                addr=addr,
                pay_method=pay_method,
                total_count= total_count,
                total_price=total_price,
                transit_price= transit_price
            )

            #todo: 用户的订单中有几个商品，需要向df_order_goods 表中加入几条记录
            conn = get_redis_connection("default")
            cart_key = "cart_%d"% user.id
            sku_ids=sku_ids.split(",")
            for sku_id in sku_ids:
                #获取商品的信息
                try:
                    # sku=GoodsSKU.objects.get(id=sku_id)
                    # 先点提交订单的这个用户先拿到的锁，后点击的这个用户堵塞。
                    # 等到先点的那个用户释放锁以后，也就是30秒后，后点的那个用户才可以往下执行代码。
                    # select_for_update() 悲观锁
                    sku = GoodsSKU.objects.select_for_update().get(id=sku_id)
                except Exception as e:
                    #商品不存在
                    transaction.savepoint_rollback(save_id) #回滚到保存点
                    return JsonResponse({"res": 4, "errmsg": "商品不存在"})
                #从redis中获取用户所要购买的商品的数量
                count = conn.hget(cart_key,sku_id)

                #todo:判断商品的库存
                if int(count) > sku.stock:
                    transaction.savepoint_rollback(save_id)  # 回滚到保存点
                    return JsonResponse({"res": 6, "errmsg": "商品库存不足"})


                #todo: 向df_order_goods 表中添加一条记录
                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=count,
                    price=sku.price
                )
                #todo:更新商品的库存和销量
                sku.stock -= int(count)
                sku.sales += int(count)
                sku.save()
                #todo:累加计算订单商品的总数量和总价格
                amount=sku.price * int(count)
                total_count += int(count)
                total_price += amount

            #todo:更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)  # 回滚到保存点
            return JsonResponse({"res": 7, "errmsg": "下单失败"})
        #提交事务
        transaction.savepoint_commit(save_id)

        #todo 清除用户购物车中的记录[1,2,7]  *sku_ids是拆包的意思
        conn.hdel=(cart_key,*sku_ids)
        #返回应答
        return JsonResponse({"res": 5, "errmsg": "创建成功"})


class OrderCommitView(View):
    """  订单创建 运用了乐观锁"""
    #添加事务，这样的话就会要么都成功，要么都失效。
    @transaction.atomic
    def post(self,request):
        """  订单创建 """
        #判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({"res": 0, "errmsg": "请先登录"})
        # 接收参数
        addr_id = request.POST.get('addr_id')
        pay_method = request.POST.get("pay_method")
        sku_ids=request.POST.get("sku_ids")  #注意获取的是cart.html页面form里的sku_ids，传给在前端模板提交订单那
        # 数据校验
        if not all([addr_id,pay_method,sku_ids]):
            return JsonResponse({"res": 1, "errmsg": "数据不完整"})
        #校验支付方式
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({"res": 2, "errmsg": "非法的支付方式"})
        #校验地址
        try:
            addr = Address.objects.get(id=addr_id)
        except Address.DoesNotExist:
            #地址不存在
            return JsonResponse({"res": 3, "errmsg": "地址非法"})
        #todo : 创建订单核心业务
        #组织参数
        #订单id : 20171122181630 + 用户id    时间戳
        order_id = datetime.now().strftime('%Y%m%d%H%M%S')+ str(user.id)

        #运费
        transit_price = 10
        #总数目和总金额
        total_count = 0
        total_price = 0

        #设置事务的保存点
        save_id = transaction.savepoint()
        try:
            #todo: 向df_order_info 表中添加一条记录
            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                addr=addr,
                pay_method=pay_method,
                total_count= total_count,
                total_price=total_price,
                transit_price= transit_price
            )

            #todo: 用户的订单中有几个商品，需要向df_order_goods 表中加入几条记录
            conn = get_redis_connection("default")
            cart_key = "cart_%d"% user.id
            sku_ids=sku_ids.split(",")
            for sku_id in sku_ids:
                for i in range(3):   #循环3遍  0 1 2
                    #获取商品的信息
                    try:
                        sku=GoodsSKU.objects.get(id=sku_id)
                    except Exception as e:
                        #商品不存在
                        transaction.savepoint_rollback(save_id) #回滚到保存点
                        return JsonResponse({"res": 4, "errmsg": "商品不存在"})
                    #从redis中获取用户所要购买的商品的数量
                    count = conn.hget(cart_key,sku_id)

                    #todo:判断商品的库存
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(save_id)  # 回滚到保存点
                        return JsonResponse({"res": 6, "errmsg": "商品库存不足"})

                    # todo:更新商品的库存和销量
                    # sku.stock -= int(count)
                    # sku.sales += int(count)
                    # sku.save()
                    orgin_stock = sku.stock
                    new_stock = orgin_stock - int(count)
                    new_sales = sku.sales + int(count)

                    #返回受影响的行数
                    res = GoodsSKU.objects.filter(id=sku_id,stock=orgin_stock).update(stock=new_stock,sales=new_sales)
                    if res ==0:  #如果返回的值为0，上边没查到数据
                        if i ==2:       #循环3遍  0 1 2，如果没有3遍，继续循环
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({"res":7,"errmsg":"又下单失败"})
                        continue

                    #todo: 向df_order_goods 表中添加一条记录
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=count,
                        price=sku.price
                    )

                    #todo:累加计算订单商品的总数量和总价格
                    amount=sku.price * int(count)
                    total_count += int(count)
                    total_price += amount
                    #跳出循环
                    break

            #todo:更新订单信息表中的商品的总数量和总价格
            order.total_count = total_count
            order.total_price = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)  # 回滚到保存点
            return JsonResponse({"res": 7, "errmsg": "下单失败"})
        #提交事务
        transaction.savepoint_commit(save_id)

        #todo 清除用户购物车中的记录[1,2,7]  *sku_ids是拆包的意思
        conn.hdel=(cart_key,*sku_ids)
        #返回应答
        return JsonResponse({"res": 5, "errmsg": "创建成功"})

# ajax post
# 前端传递的参数：订单id(order_id)
# /order/pay
class OrderPayView(View):
    """   订单支付   """
    def post(self, request):
        """   订单支付   """
        # 用户是否登录
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({"res": 0, "errmsg": "用户未登录"})

        # 接收参数
        order_id = request.POST.get('order_id')

        # 校验参数
        if not order_id:
            return JsonResponse({"res": 1, "errmsg": "无效的订单id"})
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res": 2, "errmsg": "订单错误"})
        #初始化
        alipay = AliPay(
            appid="2016092100565792",  #沙箱模式中的appid
            app_notify_url=None,  # 默认回调url  （和下面的return_url和notify_url配合使用）
            app_private_key_string=open("apps/order/app_private_key.pem").read(),
            alipay_public_key_string=open("apps/order/alipay_public_key.pem").read(),  # alipay public key, do not use your public key!
            sign_type = "RSA2",  # RSA or RSA2
            debug = True  # False by default  配合沙箱环境使用
        )
        #粘贴的网站上的电脑支付
        #借助alipay对象，向支付宝发起支付请求
        total_pay=order.total_price + order.transit_price
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id, #订单id
            total_amount=str(total_pay), #支付总金额
            subject="天天生鲜%s" % order_id, #订单描述信息
            return_url=None,  #可写将来公司的域名
            notify_url=None  # this is optional，不写，默认回调app_notify_url路径
        )
        #返回应答
        #请求接口传参
        pay_url="https://openapi.alipaydev.com/gateway.do?" + order_string  #沙箱环境加上dev
        return JsonResponse({"res": 3, "pay_url":pay_url})

class  CheckPayView(View):
    """  查看订单支付的结果 """
    def post(self,request):
        """  查询支付结果 """
        #判断用户是否登录
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({"res": 0, "errmsg": "请先登录"})
        #接收参数
        order_id = request.POST.get("order_id")
        # 校验参数
        if not order_id:
            return JsonResponse({"res": 1, "errmsg": "无效的订单id"})
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, pay_method=3, order_status=1)
        except OrderInfo.DoesNotExist:
            return JsonResponse({"res": 2, "errmsg": "订单错误"})
        # 初始化
        alipay = AliPay(
            appid="2016092100565792",  #沙箱模式中的appid
            app_notify_url=None,  # 默认回调url  （和下面的return_url和notify_url配合使用）
            app_private_key_string=open("apps/order/app_private_key.pem").read(),
            alipay_public_key_string=open("apps/order/alipay_public_key.pem").read(),
            # alipay public key, do not use your public key!
            sign_type="RSA2",  # RSA or RSA2
            debug=True  # False by default  配合沙箱环境使用
        )
        #调用支付宝的交易查询接口
        # response = {
            #是ctrl + 左击 进入alipay.api_alipay_trade_page_pay，这个返回的数据
        #     "alipay_trade_query_response": {
        #         "trade_no": "2017032121001004070200176844",  #支付宝的交易号
        #         "code": "10000",  #接口调用是否成功，可看沙箱开放环境文档
        #         "invoice_amount": "20.00",
        #         "open_id": "20880072506750308812798160715407",
        #         "fund_bill_list": [
        #             {
        #                 "amount": "20.00",
        #                 "fund_channel": "ALIPAYACCOUNT"
        #             }
        #         ],
        #         "buyer_logon_id": "csq***@sandbox.com",
        #         "send_pay_date": "2017-03-21 13:29:17",
        #         "receipt_amount": "20.00",
        #         "out_trade_no": "out_trade_no15",
        #         "buyer_pay_amount": "20.00",
        #         "buyer_user_id": "2088102169481075",
        #         "msg": "Success",
        #         "point_amount": "0.00",
        #         "trade_status": "TRADE_SUCCESS",
        #         "total_amount": "20.00"
        #     },
        #     "sign": ""
        # }
        while True:
            response=alipay.api_alipay_trade_query(order_id)
            code=response.get("code")
            if code == "10000" and response.get("trade_status") == "TRADE_SUCCESS":
                #支付成功
                #先来获取支付宝的交易流水号
                trade_no = response.get("trade_no")
                #更新数据库的订单表--交易流水号字段
                order.trade_no = trade_no
                # 更新数据库的订单表--订单状态字段
                order.order_status = 4 #待评价
                order.save()
                return JsonResponse({"res": 3, "errmsg": "支付成功"})
            elif code == "40004" or(response.get("trade_status") == "WAIT_BUYER_PAY"):
                #等待买家付款
                #业务处理失败，可能一会就会成功
                import time
                time.sleep(5)
                continue
            else:
                #支付出错
                return JsonResponse({"res": 4, "errmsg": "支付失败"})

class CommentView(LoginRequiredMixin,View):
    """  订单评论"""
    def get(self,request,order_id):
        """  提供评论页面"""
        #获取登录用户信息
        user= request.user
        #校验参数
        if not order_id:
            return redirect(reverse("user:order"))
        try:
            order= OrderInfo.objects.get(order_id= order_id,user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        #根据订单的状态获取订单的状态标题
        order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
        #获取订单商品信息
        order_skus=OrderGoods.objects.filter(order_id= order_id)
        for order_sku in order_skus:
            #计算商品的小计
            amount = order_sku.count * order_sku.price
            #动态给order_sku 增加属性 amount 保存商品小计
            order_sku.amount = amount
        #动态给order增加属性order_skus，保存订单商品信息
        order.order_skus = order_skus
        #使用模板
        return render(request,"order_comment.html",{"order":order})

    def post(self,request,order_id):
        """  处理评论内容 """
        # 获取登录用户信息
        user = request.user
        # 校验参数
        if not order_id:
            return redirect(reverse("user:order"))
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user)
        except OrderInfo.DoesNotExist:
            return redirect(reverse("user:order"))
        #获取评论条数
        total_count = request.POST.get("total_count")
        total_count = int(total_count)

        for i in range(1,total_count + 1):
            #获取评论的商品的id
            sku_id = request.POST.get("sku_%d" % i)
            #获取评论的商品的内容
            content = request.POST.get("content_%d" % i,'')
            try:
                order_goods= OrderGoods.objects.get(order=order,sku_id=sku_id)
            except OrderGoods.DoesNotExist:
                continue
            order_goods.comment = content
            order_goods.save()
        order.order_status =5 #已完成
        order.save()
        return  redirect(reverse("user:order",kwargs={"page":1}))






































