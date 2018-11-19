# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_data, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
#Ak sk 密钥，在官网上的个人中心-密钥管理那
access_key = '8NV_iPDRqLXa6_ItCWJFNOp9opcBaCuoDibSduP5'
secret_key = 'UitWCO5yo7wpBSOJTNAo8u_BxO6S9r1koZjgJlbj'

def storage(file_data):
    """
    上传文件到七牛
    :param file_data:  要上传的文件数据（二进制的）
    :return:
    """
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间,自己建的空间
    bucket_name = 'ihome-1807'


    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    ret, info = put_data(token, None, file_data)
    print(info)
    print("*"*10)
    print(ret)
    if info.status_code == 200:
        #表示上传成功，返回文件名
        return ret.get("key")
    else:
        raise Exception("上传七牛云失败")

if __name__=="__main__":
    with open("./meet.jpg","rb") as f:   #以二进制只读的形式
        file_data=f.read()
        ming=storage(file_data) #调用函数
        print(ming)  #可拿到图片的值
