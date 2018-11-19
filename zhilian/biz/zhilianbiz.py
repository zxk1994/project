from biz import base
from utils import util
import json, re, time


class ZhilianBiz(base.Base):
    def __init__(self):
        base.Base.__init__(self)

    def main(self):
        """  爬取10页数据  传参，根据网站 network"""
        for i in range(1, 11):
            url = "https://fe-api.zhaopin.com/c/i/sou" #network只截取了路由，其余的是参数
            last = {"p": i, "jl": "565", "kw": "python", "kt": "3"}
            params = {"start": (i - 1) * 60,   #分析数据得知 0 60 120
                      "pageSize": "60",
                      "cityId": "565",
                      "workExperience": "-1",
                      "education": "-1",
                      "companyType": "-1",
                      "employmentType": "-1",
                      "jobWelfareTag": "-1",
                      "kw": "python",
                      "kt": "3",
                      "lastUrlQuery": last,
                      "_v": "0.86943501",
                      "x-zp-page-request-id": "eb6cd7e33e0c422e8e3541da18398abc-1540517294335-166898"}
            self.__main(url=url, parms=params) #给下面的__main 私有方法传参


    def __main(self, url, parms):
        """ 爬取数据"""
        util.logger.warning("正在爬取%s" % url)
        r = util.get(url,params=parms)
        #如果没有得到结果，再爬取一遍，还没有，返回false截止
        if r[0] == 0:
            r = util.get(url,params=parms)
        if r[0] == 0:
            return False
        # 网页上抓包得到的数据，看网页network分析
        body = r[1].decode()
        jsondata = json.loads(body)["data"]["results"]
        for item in jsondata:
            self.posName = item["jobName"]
            self.url = item["positionURL"]
            self.salary = item["salary"]
            self.workExp = item["workingExp"]["name"]
            self.edu = item["eduLevel"]["name"]
            self.company = item["company"]["name"]
            # 1. 去重  url地址
            rs = self.getDataByUrl()
            if rs == True:
                continue
            # 2. 反爬
            time.sleep(2)
            self.__detail() #调用爬取职位描述
            self.insertData() #调用函数数据库的， 入库

    def __detail(self):
        """ 爬取职位描述"""
        util.logger.warning("正在爬取明细页面%s"%self.url)
        r = util.get(self.url)
        if r[0] == 0:
            r = util.get(self.url)
        if r[0] == 0:
            return False
        body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
        comname = re.findall('class="pos-ul">(.*?)</div>', body)
        # 无论是哪种提取类型，都有可能会出现匹配失败的问题吧,长度大于0
        if len(comname) > 0:
            self.detail = comname[0]
