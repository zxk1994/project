from dao import hoteldao  #导入hoteldao表
from utils import util

class Base():
    """  初始化"""
    def __init__(self):
        self.price = ''
        self.title = ''

    def insertData(self):
        """ 传递参数给hoteldao"""
        body=util.getBody(self.title) #去除标题的特殊符号,要不会错乱
        hoteldao.insertHotel(price=self.price, title=body)
        #插入完一次数据，需要再清空下，要不下次没有的数据，还是保存到上次的数据
        self.price = ''
        self.title = ''