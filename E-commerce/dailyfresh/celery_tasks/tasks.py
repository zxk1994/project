from django.conf import settings
from django.core.mail import send_mail
from celery import Celery  #导入celery包

from django.template import loader,RequestContext

# 给虚拟机传项目时，加上这4行，在windows上不用，注释掉
import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh1807.settings")
# django.setup()

# 注意着两个包的位置，必须在初始化底下，页面静态化使用的
from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection  #官网有方法导入redis包



#定义异步发送邮件任务1
# 创建Celery类对象
app=Celery("celery_tasks.tasks",broker="redis://192.168.163.129:6379/8")
@app.task
def send_register_active_email(to_email,username,token):
    # 开始真正的发邮件
    subject = "天天生鲜欢迎你使用"
    # message  发送邮件的内容
    message = ""  # 这个不能删掉，默认是第二个参数
    # 下面的这个就可以解析前端代码了
    html_message = "<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面的链接激活您的账户<br>" \
                   "<a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>" \
                   % (username, token, token)

    sender = settings.EMAIL_FROM  # 获取settings里的发送者信息
    receiver = [to_email]  # 此处是个列表，填写对方的邮箱，这里的email是获取的文本框的值，可给多人发送
    # 最后的html_message=html_message，前面的那个底层代码html_message=，缺省参数放在最后，后面那个是传递的值
    # 查看send_mail底层代码  ctrl+鼠标左击
    send_mail(subject, message, sender, receiver, html_message=html_message)  # 发送邮件的方式，整合

#定义页面静态化任务2
@app.task
def generate_static_index_html():
    """ 产生首页静态页面 """
    # 1、获取商品的种类信息
    types = GoodsType.objects.all()
    # 2、获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by("index")
    # 3、获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by("index")

    # 4、获取首页分类商品展示信息,（中间表链接）限制查询四个，用切片
    for type in types:
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by("index")[0:4]
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by("index")[0:4]
        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织模板上下文
    context = {
        "types": types,
        "goods_banners": goods_banners,
        "promotion_banners": promotion_banners,
    }

    # return render(request, "index.html", context)
   #使用模板，类似上面这句命令
   #1、加载模板文件，返回模板对象
    temp=loader.get_template("static_index.html")
    #2、渲染模板
    static_index_html=temp.render(context)
    #生成首页对应的静态文件,以只读的方式写文件，没有会自动生成,下面别写错了
    save_path=os.path.join(settings.BASE_DIR,"static/index.html")
    with open(save_path,"w")as f:
        f.write(static_index_html)


