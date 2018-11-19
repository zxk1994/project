#coding:utf-8
#要想能够调试，使用下面的两行命令
#这个zhilian对应的是zhilian.py 文件里的ZhilianSpider 类里的name
# from scrapy import cmdline
# cmdline.execute("scrapy crawl guaziredis".split())


import redis
from myproject import settings
r=redis.StrictRedis(host=settings.REDIS_HOST,port=settings.REDIS_PORT)
url='https://www.guazi.com/sjz/dazhong/'
r.lpush("guazicrawl2:start_urls",url)