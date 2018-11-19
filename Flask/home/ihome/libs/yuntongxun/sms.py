#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '8a216da8662360a40166586b955b10d0'

#主帐号Token
accountToken= 'f382ea179b9c4455badf1df3ca77e427'

#应用Id
appId='8a216da8662360a40166586b95ba10d7'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id

# def sendTemplateSMS(to,datas,tempId):
#
#     #初始化REST SDK
#     rest = REST(serverIP,serverPort,softVersion)
#     rest.setAccount(accountSid,accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to,datas,tempId)
#     for k,v in result.iteritems():
#
#         if k=='templateSMS' :
#                 for k,s in v.iteritems():
#                     print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)

#sendTemplateSMS(手机号码,内容数据,模板Id)


class CCP(object):
    """  把上述方法改成类的形式,用单例模式，只初始化一次就行"""
    #用来保存对象的类属性
    __instance=None
    def __new__(cls, *args, **kwargs):
        #判断CCP有没有创建好的对象，如果没有，创建一个对象进行保存
        #如果有，直接返回保存的对象
        if cls.__instance is None:
            obj=super(CCP,cls).__new__(cls)

            # 初始化REST SDK
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls.__instance=obj  #保存一下
        return cls.__instance

    def send_template_sms(self,to, datas, tempId):

        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        #想返回有用数据
        status_code=result.get("statusCode")
        if status_code == "000000":
            #发送短信成功
            return 0
        else:
            #发送失败
            return -1


if __name__ == "__main__":
    ccp=CCP()
    #手机号码,  内容数据(特殊[验证码内容 ，过期时间在这5分钟]),  模板Id测试是1
    ccp.send_template_sms("15231128853",["1124","5"],1)