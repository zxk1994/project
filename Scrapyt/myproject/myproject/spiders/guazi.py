# -*- coding: utf-8 -*-
#爬取时需要cooking重新换换，并且settings.py 引擎的cookies需要打开
import scrapy
import json, re
from myproject.items import MyprojectItem

class GuzziSpider(scrapy.Spider):
    name = 'guazi'

    def start_requests(self):
        urls = [
            'https://www.guazi.com/sjz/dazhong/',
        ]
        heade = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                 "Accept-Encoding": "gzip, deflate, br",
                 "Accept-Language": "zh-CN,zh;q=0.9",
                 "Connection": "keep-alive",
                 "Cookie": "antipas=2H192tw893K976A23019j485050817",
                 "Host": "www.guazi.com",
                 "Referer": "https://www.guazi.com/sjz/dazhong/",
                 "Upgrade-Insecure-Requests": "1",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=heade) #调用下面的方法

    def parse(self, response):
        print('sdf')
        pass


