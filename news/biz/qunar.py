from biz import base_hotel
from utils import util
import json, re, time
from selenium import webdriver


class QuNarBiz(base_hotel.Base):
    def __init__(self):
        base_hotel.Base.__init__(self)

    # def main(self):
    #     driver = webdriver.Chrome()
    #     driver.get("http://hotel.qunar.com/city/shijiazhuang/#fromDate=2018-10-28&from=qunarindex&toDate=2018-10-29")
    #     time.sleep(2)
    #     r = driver.page_source
    #     self.__main(r)
    #     driver.close()


    def main(self):
        util.logger.warning("正在爬取%s")
        driver = webdriver.Chrome()
        driver.get("http://hotel.qunar.com/city/shijiazhuang/#fromDate=2018-10-28&from=qunarindex&toDate=2018-10-29")
        time.sleep(2)
        r = driver.page_source
        body = r.replace("\n", "").replace("\r", "").replace("\t", "")
        data = re.findall(
            '<div class="hotel_baseinfo">.*?"e_title js_list_name">(.*?)</a>.*?<cite>¥</cite><b>(.*?)</b>起</a>', body)
        if len(data) > 0:
            for item in data:
                self.title=item[0]
                self.price=item[1]
                # 2. 反爬
                time.sleep(5)
                self.insertData()
            driver.close()