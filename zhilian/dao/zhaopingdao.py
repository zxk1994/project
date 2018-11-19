from utils import util, dbmysql  #从包中导入的文件名


# 智联的dao文件
#接收 base 文件  insertData传递过来的参数
def insertZhilian(**kwargs):
    rs = None
    try:
        posId = util.getUUID()
        sql = "insert into zhaoping(posId,posName,salary,workExp,edu,company,detail,insertTime,opertionTime,url) VALUES ('%s','%s','%s','%s','%s','%s','%s',now(),now(),'%s');" % (
            posId, kwargs["posName"], kwargs["salary"], kwargs["workExp"], kwargs["edu"], kwargs["company"],
            kwargs["detail"],kwargs["url"])
        rs = dbmysql.query(sql)
    except Exception as e:
        util.logger.error(e)
    return rs


# 去重  依据url地址，判断爬取的数据重不重复，一般url地址不会重复
def getDataByUrl(url):
    rs = None
    try:
        sql = "select count(1) from zhaoping WHERE url='%s';" % url
        rs = dbmysql.first(sql)
    except Exception as e:
        util.logger.error(e)
    return rs
