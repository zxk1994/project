#coding:utf-8
from flask import Flask
from config import config_map  #导入config.py 文件的字典
from flask_sqlalchemy import SQLAlchemy  #用于操作数据库
import redis
from flask_session import Session
from flask_wtf import CSRFProtect
#下面两个是导入日志包
import logging
from logging.handlers import RotatingFileHandler  #使日志保存在文件中
from ihome.utils.commons import ReConverter #导入正则表达式包

db=SQLAlchemy()   #用于操作mysql数据库,在create_app类中初始化
redis_store=None  #链接redis数据库,在create_app类中初始化

#设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  #调试debug级
#创建日志记录器，指明日志保存的路径，每个日志文件的最大大小，保存的日志文件个数上限
file_log_handle=RotatingFileHandler("logs/log",maxBytes=1024*1024*100,backupCount=10)
#创建日志记录的格式    日志等级  输入日志信息的文件名 行数  日志信息
formatter=logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
#为刚创建的日志记录器设置日志记录格式
file_log_handle.setFormatter(formatter)
#为全局的日志工具对象（flask app 使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handle)






#工厂模式
#创建app，传参（"develop" "product"），调用config方法
def create_app(config_name):
    """
    创建flask应用对象
    ：param config_name ：str 配置模块的模式名字例如（"develop" "product"）
    :return:
    """
    app=Flask(__name__)  #创建应用
    #根据配置模块的名字获取配置参数的类
    config_class=config_map.get(config_name) #以字典的形式获取值
    app.config.from_object(config_class)  #根据值调用config.py文件中的Config类

    #使用app初始化db
    db.init_app(app)
    # 链接redis数据库，config_class相当于获得了Config类
    global redis_store  #全局变量声明一下
    redis_store = redis.StrictRedis(host=config_class.REDIS_HOST, port=config_class.REDIS_PORT)
    # 利用flask_session包，将session数据保存到redis里
    Session(app)
    # 为flask补充csrf防护
    CSRFProtect(app)

    #为flask添加自定义的转换器
    app.url_map.converters["re"]=ReConverter

    #注册蓝图
    #http://127.0.0.1:5000/api/v1.0/index
    # 或者导入 from . import api_1_0  推迟导入，防止与demo.py 冲突
    from ihome import api_1_0
    app.register_blueprint(api_1_0.api,url_prefix="/api/v1.0")
    #注册提供静态文件的蓝图
    from ihome import web_html
    app.register_blueprint(web_html.html)
    return app