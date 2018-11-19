#coding:utf-8
# demo.py 专门用来写路由和函数的
from . import api
from ihome import db,models
import logging
from flask import current_app

@api.route("/index")  #定义路由，最好在前写上/
def index():
    # 两种写法都行
    # logging.error("error") #错误级别
    # logging.warning("warning")#警告级别
    # logging.info("info") #消息提示级别
    # logging.debug("debug")#调试级别

    # current_app.logger.error("error")
    # current_app.logger.warn("warn")
    # current_app.logger.info("info")
    # current_app.logger.debug("debug")
    return ("index.page")
