# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

#固定写法 写字段
class MyprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    jobname = scrapy.Field()
    salary = scrapy.Field()
    companyName = scrapy.Field()
    gwms = scrapy.Field()
    pass


class LagouItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    jobname = scrapy.Field()
    salary = scrapy.Field()
    companyName = scrapy.Field()
    gwms=scrapy.Field()
    pass

class GuaziItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    licheng = scrapy.Field()
    url=scrapy.Field()
    pass