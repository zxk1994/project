# -*- coding: utf-8 -*-
import scrapy
import json, re
from myproject.items import GuaziItem
#导入redis分布式包
from scrapy_redis.spiders import RedisSpider



class GuzziSpider(RedisSpider):
    name = 'guaziredis'
    redis_key = 'guaziredis:start_urls'  #键名

    # def start_requests(self):
    #     yield scrapy.Request(url='http://www.guazi.com/sjz/dazhong/', callback=self.parse)
    #匹配链接的详情路由，下面得到的不完整，需要加上前面的https拼接字符串
    def parse(self, response):
        body = response.text.replace('\n', '').replace('\r', '').replace('\t', '')
        info = re.findall('<a title=".*?" href="(.*?)"', body)
        if len(info) > 0:
            for item in info:
                yield scrapy.Request(url="https://www.guazi.com%s" % item, callback=self.parse2)
        print('sdf')
        pass

    #爬取详情页面具体的信息，标题、价格、里程
    def parse2(self, response):
        body = response.text.replace('\n', '').replace('\t', '').replace('\r', '')
        title = re.findall('class="titlebox">(.*?)<span', body)
        if len(title) > 0:
            print(title[0])
        price = re.findall('class="pricestype">(.*?)<span', body)
        if len(price) > 0:
            print(price[0])
        licheng = re.findall('class="assort clearfix">.*?"two"><span>(.*?)</span>', body)
        if len(licheng) > 0:
            print(licheng[0])
        print(response.url)
