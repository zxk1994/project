import requests
import logging
import uuid   #高并发时，不会重复id

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s-%(name)s-%(levelname)s-%(filename)s-%(lineno)d] %(message)s')
logger = logging.getLogger(__name__)

def get(url, params=None, cookie=None, headers=None, proxies=None):
    '''
    此方法用于发起get请求
    :param url:
    :param params:
    :param cookie:
    :param headers:
    :param proxies:
    :return:
    '''
    s = requests.session()
    try:
        if params != None:
            s.params = params
        if cookie != None:
            s.cookies = cookie
        if headers != None:
            s.headers = headers
        if proxies != None:
            s.proxies = proxies
        r = s.get(url=url, timeout=20) #响应时间20秒
        return (1, r.content)
    except Exception as e:
        print(e)
    finally:
        if s:
            s.close()
    return (0,)


def post(url, data, params=None, cookie=None, headers=None, proxies=None):
    '''
    此方法用于发起post请求
    :param url:
    :param params:
    :param cookie:
    :param headers:
    :param proxies:
    :return:
    '''
    s = requests.session()
    try:
        if params != None:
            s.params = params
        if cookie != None:
            s.cookies = cookie
        if headers != None:
            s.headers = headers
        if proxies != None:
            s.proxies = proxies
        r = s.post(url=url, data=data, timeout=20)
        return (1, r.content,r.cookies)
    except Exception as e:
        print(e)
    finally:
        if s:
            s.close()
    return (0,)

#针对表中的id值
def getUUID():
    return str(uuid.uuid4())


def getBody(body):
    '''
    去除爬取内容的特殊符号
    :param body:
    :return:
    '''
    return body.replace("'", "‘")

