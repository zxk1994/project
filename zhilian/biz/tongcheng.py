from biz import base
from utils import util
import json, re, time
from urllib.parse import quote
from lxml import etree
from bs4 import BeautifulSoup


class TongChengBiz(base.Base):
    def __init__(self):
        base.Base.__init__(self)

    def main(self):
        """  爬取10页数据  传参，根据网站 network"""
        # for i in range(1, 11):
        url="https://bj.58.com/job/?key=python%E7%88%AC%E8%99%AB&final=1&jump=1"
        # word="爬虫"
        # url =quote("https://bj.58.com/job/?key=python%s&final=1&jump=1" % word,'utf-8') #network只截取了路由，其余的是参数
        # last = {"p": i, "jl": "565", "kw": "python", "kt": "3"}
        # params = {"start": (i - 1) * 60,   #分析数据得知 0 60 120
        #           "pageSize": "60",
        #           "cityId": "565",
        #           "workExperience": "-1",
        #           "education": "-1",
        #           "companyType": "-1",
        #           "employmentType": "-1",
        #           "jobWelfareTag": "-1",
        #           "kw": "python",
        #           "kt": "3",
        #           "lastUrlQuery": last,
        #           "_v": "0.86943501",
        #           "x-zp-page-request-id": "eb6cd7e33e0c422e8e3541da18398abc-1540517294335-166898"}
        self.__main(url=url) #给下面的__main 私有方法传参



    def __main(self, url):
        """ 爬取数据"""
        util.logger.warning("正在爬取%s" % url)
        r = util.get(url)
        #如果没有得到结果，再爬取一遍，还没有，返回false截止
        if r[0] == 0:
            r = util.get(url)
        if r[0] == 0:
            return False
        # 网页上抓包得到的数据，看网页network分析
        # body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
        # result = re.findall('<div class="job_name clearfix">.*?<a href="(.*?)".*?class="name">(.*?)</span></a>.*?="job_salary">(.*?)<i class="unit">.*?title="(.*?)"></a>.*?class="xueli">(.*?)</span>',body)
        # print(result)

        #//p[@class="job_salary"]
        # body=r[1].decode()
        # bodytree = etree.HTML(body)
        # result=bodytree.xpath("//p[@class='job_salary']/text()")

        body=r[1].decode()
        soup=BeautifulSoup(body,'lxml')
        # result = soup.select("div.job_name > a > span.name ")
        result=soup.find_all("div",class_="job_name")
        # result1 = soup.find_all("div", class_="job_comp")
        # print(result1)
        if len(result) > 0:
            for item in result:
                self.posName=item.text
                self.salary=item.next_sibling.next
                # self.url=item.contents[0].attrs["href"]
                print(self.salary)
                print(self.posName)
            # if len(result1) > 0:
            # for item1 in result1:
            #     self.company=item1.contents[2].text
            #     self.edu=item1.contents[4].contents[2].next
            #     print(self.company)
            #     print(self.edu)

               # 1. 去重  url地址
               #  rs = self.getDataByUrl()
               #  if rs == True:
               #      continue
                # 2. 反爬
                time.sleep(2)
                # self.__detail() #调用爬取职位描述
                self.insertData() #调用函数数据库的， 入库






    # def __detail(self):
    #     """ 爬取职位描述"""
    #     util.logger.warning("正在爬取明细页面%s"%self.url)
    #     r = util.get(self.url)
    #     if r[0] == 0:
    #         r = util.get(self.url)
    #     if r[0] == 0:
    #         return False
    #     body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
    #     comname = re.findall('<h2 class="title">职位描述</h2>.*?class="des">(.*?)<div class="Job requirements">', body)
    #     # 无论是哪种提取类型，都有可能会出现匹配失败的问题吧,长度大于0
    #     if len(comname) > 0:
    #         self.detail = comname[0]
