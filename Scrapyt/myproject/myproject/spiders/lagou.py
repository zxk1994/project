# -*- coding: utf-8 -*-
import scrapy
import json, re
from myproject.items import LagouItem

class LagouSpider(scrapy.Spider):
    name = 'lagou'
    head = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        # "Content-Length": "26",#不写长度，写上这个抓取不到数据
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.lagou.com",
        "Origin": "https://www.lagou.com",
        "Referer": "https://www.lagou.com/jobs/list_python?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput=",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        "X-Anit-Forge-Code": "0",
        "X-Anit-Forge-Token": "None",
        "X-Requested-With": "XMLHttpRequest",
    }

    #第二种url 方法，固定写法
    def start_requests(self):
        urls = [
            'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false',
        ]
        data = {"first": "false",
                "pn": "3",
                "kd": "python"}

        for url in urls:
            #post 方法
            yield scrapy.FormRequest(url,
                                     formdata=data,
                                     callback=self.parse,
                                     headers=self.head,
                                     # meta={"proxy": "http://ip:port"}#Scrapt加代理IP方法
                                     )
            #get 方法
            # yield scrapy.Request(url=url, callback=self.parse) #调用下面的方法

    def parse(self, response):
        jsondata = json.loads(response.text)
        data = jsondata["content"]["positionResult"]["result"]
        for item in data:
            lgitem = LagouItem()
            lgitem["companyName"] = item["companyFullName"]
            lgitem["salary"] = item["salary"]
            lgitem["jobname"] = item["positionName"]
            url = "https://www.lagou.com/jobs/%s.html" % (item["positionId"])
            #上面的想保存到数据库，下面的继续爬取别的网页 职位描述，pipelines 处理数据库
            # yield myitem  #不这样写了，就使用下面的方法 meta  给了下面的方法 关联 myitem
            yield scrapy.Request(url=url, callback=self.parse11, meta={"lgitem": lgitem}, headers=self.head)

    # 下面方法和上面关联 爬取岗位描述，利用meta 传递实例对象
    def parse11(self, response):
        lgitem = response.meta["lgitem"]
        body = response.text.replace('\n', '')
        gwzz = re.findall('class="job_bt">(.*?)</dd>', body)
        if len(gwzz) > 0:
            lgitem["gwms"] = gwzz[0]
        yield lgitem




