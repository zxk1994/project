from utils import util, dbmysql


# 公告的dao文件
def insertgonggao(**kwargs):
    rs = None
    try:
        ggId = util.getUUID()
        sql = "insert into flask(ggId,insertTime,opertionTime,title,times,body,url) VALUES ('%s',now(),now(),'%s','%s','%s','%s');" % (
            ggId, kwargs["title"], kwargs["times"], kwargs["body"], kwargs["url"])
        rs = dbmysql.query(sql)
    except Exception as e:
        util.logger.error(e)
    return rs


def getDataByUrl(url):
    rs = None
    try:
        sql = "select count(1) from flask WHERE url='%s';" % url
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs

#列表页
def getDataAll():
    rs = None
    try:
        sql = "select * from flask order BY insertTime;"
        rs = dbmysql.fetchall(sql)
    except Exception as e:
        util.logger.error(e)
    return rs

#详情页
def getDataById(id):
    rs = None
    try:
        sql = "select * from flask WHERE ggId='%s' order BY insertTime;" % id
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs

def getData():
    rs = None
    try:
        sql = "select * from flask order BY insertTime;"
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs
