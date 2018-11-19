#coding:utf-8

from flask import Blueprint
#创建蓝图对象,第一个是包名
api=Blueprint("api_1_0",__name__)

#导入蓝图的视图，从当前导入demo，初始化
from . import demo,verify_code,passport,profile,houses,orders,pay

