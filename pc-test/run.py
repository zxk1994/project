import time
import ggzywork
from utils import util
from threading import Thread

def getggzy():
    while 1:
        util.logger.error("开始")
        for i in range(1, 10000):
            ggzywork.hello.delay(i)
        util.logger.error("休眠")
        time.sleep(600)

def getyhggzy():
    for i in  range(1,10000):
        pass
t=[]
t1=Thread(target=getggzy)
t2=Thread(target=getyhggzy)
t.append(t1)
t.append(t2)

if __name__ == '__main__':
    for item in t:
        if item.is_alive()==False:
            item.start()
    # while 1:
    #     util.logger.warning("开始生产消息")
    #     getggzy()
    #     util.logger.warning('进入休眠')
    #     time.sleep(600)
        # for item in range(100000):
        #     workzhilian.hello.delay(item, item)
