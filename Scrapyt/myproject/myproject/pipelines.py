# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from myproject import settings
from myproject.items import MyprojectItem,LagouItem,GuaziItem

#下面是操作数据库的内容
class MyprojectPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(host=settings.MONGOHOST, port=settings.MONGOPORT)
        self.db = client[settings.MONGODB]  # 数据库名
    def process_item(self, item, spider):
        table = ""
        if isinstance(item, MyprojectItem):
            table = self.db.zhilian  # 集合名  isinstance 比较item 是否是 MyprojectItem里的
        # elif isinstance(item, GwItem):  # 这个其实不用了，把岗位描述放到了MyprojectItem 里 用meta传递
        #     table = self.db.gwtable
        elif isinstance(item, LagouItem):
            table = self.db.lagou
        elif isinstance(item, GuaziItem):
            table = self.db.guazi
        table.insert_one(dict(item)) #需要dict 转化一下
        print(item)
        return item



#下面的是setting配置管道时，可以一个方法存mongodb数据库，一个存mysql
# class Myproject333Pipeline(object):
#     def __init__(self):
#         client = pymongo.MongoClient()
#         self.db = client.zhilian1030
#
#     def process_item(self, item, spider):
#         table = ""
#         if isinstance(item, MyprojectItem):
#             table = self.db.zhilian
#         elif isinstance(item, GwItem):
#             table = self.db.gwtable
#         table.insert_one(dict(item))
#         print(item)
#         return item