from biz import base
from utils import util
import json, re, time


class WuYouBiz(base.Base):
    def __init__(self):
        base.Base.__init__(self)

    def main(self):
        """  爬取10页数据  传参，根据网站 network"""
        for i in range(1, 3):
            url = "https://search.51job.com/list/160200,000000,0000,00,9,99,python,2,%s.html?" %i #network只截取了路由，其余的是参数

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
        body = r[1].decode("gbk").replace('\n', '').replace('\r', '').replace('\t', '')

        result = re.findall(
            '<div class="el">.*?_blank" title="(.*?)" href="(.*?)" onmousedown="">.*?<a target="_blank" title="(.*?)".*? <span class="t4">(.*?)</span>',
            body)

        if len(result) > 0:
            for item in result:
                self.posName=item[0]
                self.url=item[1]
                self.company=item[2]
                self.salary=item[3]
                # 1. 去重  url地址
                rs = self.getDataByUrl()
                if rs == True:
                    continue
                # 2. 反爬
                time.sleep(5)
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
        body = r[1].decode("gbk").replace('\n', '').replace('\r', '').replace('\t', '')
        comname = re.findall('<p>岗位职责：</p>(.*?)<div class="mt10">', body)
        # 无论是哪种提取类型，都有可能会出现匹配失败的问题吧,长度大于0
        if len(comname) > 0:
            self.detail = comname[0]
