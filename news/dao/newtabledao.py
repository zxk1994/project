from utils import util, dbmysql  #从包中导入的文件名


# 凤凰网的dao文件
#接收 base 文件  insertData传递过来的参数
def insertZhilian(**kwargs):
    rs = None
    try:
        id = util.getUUID()
        sql = "insert into newtable(id,date,title,url,insertTime,opertionTime) VALUES ('%s','%s','%s','%s',now(),now());" % (
            id, kwargs["date"], kwargs["title"], kwargs["url"])
        rs = dbmysql.query(sql)
    except Exception as e:
        util.logger.error(e)
    return rs


# 去重  依据url地址，判断爬取的数据重不重复，一般url地址不会重复
def getDataByUrl(url):
    rs = None
    try:
        sql = "select count(1) from newtable WHERE url='%s';" % url
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs
