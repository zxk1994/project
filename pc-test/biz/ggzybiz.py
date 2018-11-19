from biz import base
from utils import util
import json, re, time
import datetime


class GgzyBiz(base.Base):
    def __init__(self):
        base.Base.__init__(self)
        self.__headers = {"Accept": "application/json, text/javascript, */*; q=0.01",
                          "Accept-Encoding": "gzip, deflate",
                          "Accept-Language": "zh-CN,zh;q=0.9",
                          "Connection": "keep-alive",
                          "Content-Length": "242",
                          "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                          "Host": "deal.ggzy.gov.cn",
                          "Origin": "http://deal.ggzy.gov.cn",
                          "Referer": "http://deal.ggzy.gov.cn/ds/deal/dealList.jsp",
                          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                          "X-Requested-With": "XMLHttpRequest"}

    def main(self, page):
        s = time.strftime("%Y-%m-%d", time.localtime())
        url = "http://deal.ggzy.gov.cn/ds/deal/dealList_find.jsp"
        data = {"TIMEBEGIN_SHOW": "2018-10-28",
                "TIMEEND_SHOW": s,
                "TIMEBEGIN": "2018-10-28",
                "TIMEEND": s,
                "DEAL_TIME": "02",
                "DEAL_CLASSIFY": "00",
                "DEAL_STAGE": "0000",
                "DEAL_PROVINCE": "0",
                "DEAL_CITY": "0",
                "DEAL_PLATFORM": "0",
                "DEAL_TRADE": "0",
                "isShowAll": "1",
                "PAGENUMBER": page,
                "FINDTXT": "",
                "validationCode": "", }

        if self.__main(url=url, data=data) == False:
            return False

    def __main(self, url, data):
        util.logger.warning("正在爬取%s" % url)
        r = util.post(url, data=data, headers=self.__headers)
        if r[0] == 0:
            r = util.post(url, data=data, headers=self.__headers)
        if r[0] == 0:
            return False
        body = r[1].decode().replace(' ', '')
        jsondata = json.loads(body)["data"]

        for item in jsondata:
            self.url = item["url"].replace("/a/", '/b/')
            self.title = item["titleShow"]
            self.times = item["timeShow"]
            # 时间判断
            if util.timepd(self.times) == False:
                return False
            # 1. 去重  url地址
            rs = self.getDataByUrl()
            if rs == True:
                continue
            # 2. 反爬
            time.sleep(2)
            self.__detail()
            self.insertData()

    def __detail(self):
        util.logger.warning("正在爬取明细页面%s" % self.url)
        r = util.get(self.url, headers=self.__headers)
        if r[0] == 0:
            r = util.get(self.url, headers=self.__headers)
        if r[0] == 0:
            return False
        body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
        body2 = re.findall('class="detail_content">(.*?)<script>', body)
        # 无论是哪种提取类型，都有可能会出现匹配失败的问题吧
        if len(body2) > 0:
            self.body = body2[0]
