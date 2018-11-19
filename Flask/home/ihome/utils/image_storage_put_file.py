# -*- coding: utf-8 -*-
# flake8: noqa

from qiniu import Auth, put_file, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = '8NV_iPDRqLXa6_ItCWJFNOp9opcBaCuoDibSduP5'
secret_key = 'UitWCO5yo7wpBSOJTNAo8u_BxO6S9r1koZjgJlbj'

def storage(file_name):
    """
    #上传文件到七牛云
    :param file_name: 要上传的文件的路径及名字
    :return:
    """
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihome-1807'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)
    ret, info = put_file(token, None, localfile)
    if info.status_code == 200:
        #表示上传成功，返回文件名
        return ret.get("key")
    else:
        raise Exception("上传七牛云失败")


if __name__=="__main__":
    # 要上传文件的本地路径
    localfile = './meet.jpg'
    ming=storage(localfile)
    print(ming)
