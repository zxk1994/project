#coding:utf-8
import redis
# import pymysql
# pymysql.install_as_MySQLdb()



class Config(object):
    """ 配置信息"""
    # DEBUG=True   #开启调试模式，有错会报错
    SECRET_KEY="zhangzhangsssskkf"
    #配置mysql数据库，名字固定的
    SQLALCHEMY_DATABASE_URI="mysql://root:root@192.168.163.129:3306/ihome_1807"
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    #操作redis,名字自己起的
    REDIS_HOST="192.168.163.129"
    REDIS_PORT=6379
    #配置flask_session
    SESSION_TYPE="redis"
    SESSION_REDIS=redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER=True  #对cookie中的session_id 进行隐藏处理
    PERMANENT_SESSION_LIFETIME=86400 #session 数据的有效期 秒  1天

class DevelopmentConfig(Config):
    """  开发环境"""
    DEBUG=True   #开启调试模式，有错会报错，还可自动重启

class ProductionConfig(Config):
    """  上线环境"""
    pass

#新建个字典，可在前传参的时候调用上述环境
config_map={
    "develop":DevelopmentConfig,
    "product":ProductionConfig
}