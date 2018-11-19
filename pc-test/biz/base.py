from dao import gonggaodao
from utils import util


class Base():
    def __init__(self):
        self.url = ''
        self.title = ''
        self.times = ''
        self.body = ''

    def getDataByUrl(self):
        try:
            rs = gonggaodao.getDataByUrl(self.url)
            if rs[0] > 0:
                return True
            else:
                return False
        except Exception as e:
            util.logger.error(e)

    def insertData(self):
        body = util.getBody(self.body)
        gonggaodao.insertgonggao(url=self.url, title=self.title, times=self.times, body=body)
        self.url = ''
        self.title = ''
        self.times = ''
        self.body = ''
