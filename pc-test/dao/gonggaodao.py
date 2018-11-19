from utils import util, dbmysql


# 公告的dao文件
def insertgonggao(**kwargs):
    rs = None
    try:
        ggId = util.getUUID()
        sql = "insert into gonggaobody(ggId,insertTime,opertionTime,title,times,body,url) VALUES ('%s',now(),now(),'%s','%s','%s','%s');" % (
            ggId, kwargs["title"], kwargs["times"], kwargs["body"], kwargs["url"])
        rs = dbmysql.query(sql)
    except Exception as e:
        util.logger.error(e)
    return rs


def getDataByUrl(url):
    rs = None
    try:
        sql = "select count(1) from gonggaobody WHERE url='%s';" % url
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs


def getDataAll():
    rs = None
    try:
        sql = "select * from gonggaobody order BY insertTime;"
        rs = dbmysql.fetchall(sql)
    except Exception as e:
        util.logger.error(e)
    return rs


def getDataById(id):
    rs = None
    try:
        sql = "select * from gonggaobody WHERE ggId='%s' order BY insertTime;" % id
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs

def getData():
    rs = None
    try:
        sql = "select * from gonggaobody order BY insertTime;"
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs
