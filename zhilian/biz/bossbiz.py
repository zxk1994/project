from biz import base
from utils import util
import json, re, time

class BossBiz(base.Base):
    def __init__(self):
        base.Base.__init__(self)
        self.__headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
        #如果不能用，加个代理ip
        self.__proxies ={
            "http": "http://115.46.73.229:8123",
            "https": "http://115.46.73.229:8123",
        }

    def main(self):
        for i in range(1, 11):
            url = "https://www.zhipin.com/c101010100/?query=python&page=%s&ka=page-%s" % (i, i)
            self.__main(url)

    def __main(self, url):
        util.logger.warning("正在爬取%s" % url)
        r = util.get(url, headers=self.__headers,proxies=self.__proxies)
        if r[0] == 0:
            r = util.get(url)
        if r[0] == 0:
            return False
        body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
        result = re.findall(
            'class="job-primary">.*?href="(.*?)".*?job-title">(.*?)</div>.*?"red">(.*?)</span>.*?</em>(.*?)<em.*?/em>(.*?)</p>.*?blank">(.*?)</a>',
            body)
        if len(result) > 0:
            for item in result:
                self.posName = item[1]
                self.url = "https://www.zhipin.com%s" % item[0]
                self.salary = item[2]
                self.workExp = item[3]
                self.edu = item[4]
                self.company = item[5]
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
        r = util.get(self.url,headers=self.__headers)
        if r[0] == 0:
            r = util.get(self.url,headers=self.__headers)
        if r[0] == 0:
            return False
        body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
        comname = re.findall('<h3>职位描述</h3>(.*?)</div>', body)
        # 无论是哪种提取类型，都有可能会出现匹配失败的问题吧
        if len(comname) > 0:
            self.detail = comname[0]
