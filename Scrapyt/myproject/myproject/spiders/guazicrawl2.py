# -*- coding: utf-8 -*-
import scrapy
import json, re
from myproject.items import GuaziItem
#导入深度爬虫包
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider #导入scrapy_redis包

class GuzziSpider(RedisCrawlSpider):
    name = 'guazicrawl2'
    redis_key = 'guazicrawl2:start_urls'

    # start_urls = ['http://www.guazi.com/sjz/dazhong/']
    #只能匹配url
    rules = (
        # 提取匹配 页数的url  的链接并跟进链接(没有callback意味着follow默认为True)
        Rule(LinkExtractor(allow=('/sjz/dazhong/o\d+/#bread',))),

        # 提取匹配点击大众车名进入详情页面的链接并使用spider的parse_item方法进行分析
        Rule(LinkExtractor(allow=('/sjz/\w{17}\.htm#fr_page=list&fr_pos=city&fr_no=\d+',)), callback='parse_item'),
    )

    # 爬取详情页面具体的信息，标题、价格、里程、url
    def parse_item(self, response):
        guazi = GuaziItem() #需要在item内重新定义个类，并且写字段
        body = response.text.replace('\n', '').replace('\t', '').replace('\r', '')
        title = re.findall('class="titlebox">(.*?)<span', body)
        if len(title) > 0:
            guazi["name"] = title[0]
        price = re.findall('class="pricestype">(.*?)<span', body)
        if len(price) > 0:
            guazi["price"] = price[0]
        licheng = re.findall('class="assort clearfix">.*?"two"><span>(.*?)</span>', body)
        if len(licheng) > 0:
            guazi["licheng"] = licheng[0]
        guazi["url"] = response.url
        yield guazi


