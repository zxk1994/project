from dao import newtabledao  #导入newtabledao表
from utils import util

class Base():
    """  初始化"""
    def __init__(self):
        self.url = ''
        self.date = ''
        self.title = ''

    def insertData(self):
        """ 传递参数给newtabledao.insertZhilian"""
        body=util.getBody(self.title) #去除标题的特殊符号,要不会错乱
        newtabledao.insertZhilian(url=self.url, date=self.date, title=body)
        #插入完一次数据，需要再清空下，要不下次没有的数据，还是保存到上次的数据
        self.url = ''
        self.date = ''
        self.title = ''


    def getDataByUrl(self):
        """  传递路由 给newtabledao 文件的getDataByUrl方法 去重需要传递url"""
        try:
            rs = newtabledao.getDataByUrl(self.url)
            if rs[0] > 0:
                return True
            else:
                return False
        except Exception as e:
            util.logger.error(e)
