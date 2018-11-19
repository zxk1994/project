from biz import base
from utils import util
import json, re, time

class IfengBiz(base.Base):
    def __init__(self):
        base.Base.__init__(self)

    def main(self):
        for i in range(5, 7):
            url = "http://news.ifeng.com/listpage/11502/2018102%s/1/rtlist.shtml"%i
            self.__main(url)

    def __main(self, url):
        util.logger.warning("正在爬取%s" % url)
        r = util.get(url)
        if r[0] == 0:
            r = util.get(url)
        if r[0] == 0:
            return False
        body = r[1].decode().replace('\n', '').replace('\r', '').replace('\t', '')
        result = re.findall(
            '<li><h4>(.*?)</h4><a href=(.*?)target="_blank">(.*?)</a></li>',
            body)
        if len(result) > 0:
            for item in result:
                # print(item)
                self.date = item[0]
                self.url = item[1]
                self.title = item[2]
                # 1. 去重  url地址
                rs = self.getDataByUrl()
                if rs == True:
                    continue
                # 2. 反爬
                time.sleep(5)
                self.insertData()