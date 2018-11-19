# -*- coding: utf-8 -*-
import scrapy
import json, re
from myproject.items import MyprojectItem

class ZhilianSpider(scrapy.Spider):
    name = 'zhilian'
    #第一种url 方法
    # start_urls = ['http://quotes.toscrape.com/page/1/',
    #               'http://quotes.toscrape.com/page/2/', ]
    #第二种url 方法，固定写法
    def start_requests(self):
        urls = [
            'https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=530&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kw=python&kt=3&lastUrlQuery=%7B%22jl%22:%22530%22,%22kw%22:%22python%22,%22kt%22:%223%22%7D&_v=0.22712104&x-zp-page-request-id=9be8ca5eccf34b7da20009fd3b29a9c0-1540864422359-483615',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse) #调用下面的方法

    def parse(self, response):
        jsondata = json.loads(response.text)
        result = jsondata["data"]["results"]
        for item in result:
            myitem = MyprojectItem() #实例化对象，需要调用items.py的MyprojectItem()
            deurl = item["positionURL"]
            myitem["jobname"] = item["jobName"]
            myitem["salary"] = item["salary"]
            myitem["companyName"] = item["company"]["name"]
            #上面的想保存到数据库，下面的继续爬取别的网页 职位描述，pipelines 处理数据库
            # yield myitem  #不这样写了，就使用下面的方法 meta  给了下面的方法 关联 myitem
            yield scrapy.Request(deurl, callback=self.parse22, meta={"istem": myitem})

    # 下面方法和上面关联 爬取岗位描述，利用meta 传递实例对象
    def parse22(self, response):
        myitem = response.meta["istem"]
        body = response.text.replace("\n", '')
        info = re.findall('class="pos-ul">(.*?)</div>', body)
        # myitem = GwItem() 利用meta 就不用GwItem单独写了
        if len(info) > 0:
            myitem["gwms"] = info[0]
        yield myitem




