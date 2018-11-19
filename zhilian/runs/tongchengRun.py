from biz import tongcheng
import time
from utils import util

if __name__ == '__main__':
    while 1:
        util.logger.warning("开始爬取")
        zh = tongcheng.TongChengBiz()
        zh.main()
        util.logger.warning("休眠")
        time.sleep(10)
