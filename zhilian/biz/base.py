from dao import zhaopingdao  #导入zhaopingdao表
from utils import util

class Base():
    """  初始化"""
    def __init__(self):
        self.url = ''
        self.posName = ''
        self.salary = ''
        self.workExp = ''
        self.edu = ''
        self.company = ''
        self.detail = ''


    def insertData(self):
        """ 传递参数给zhaopingdao.insertZhilian"""
        body=util.getBody(self.detail) #去除职位描述的特殊符号,要不会错乱
        zhaopingdao.insertZhilian(url=self.url, posName=self.posName, salary=self.salary, workExp=self.workExp,
                                      edu=self.edu, company=self.company, detail=body)
        #插入完一次数据，需要再清空下，要不下次没有的数据，还是保存到上次的数据
        self.url = ''
        self.posName = ''
        self.salary = ''
        self.workExp = ''
        self.edu = ''
        self.company = ''
        self.detail = ''


    def getDataByUrl(self):
        """  传递路由 给zhaopingdao 文件的getDataByUrl方法 去重需要传递url"""
        try:
            rs = zhaopingdao.getDataByUrl(self.url)
            if rs[0] > 0:
                return True
            else:
                return False
        except Exception as e:
            util.logger.error(e)
