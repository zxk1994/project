from utils import util, dbmysql  #从包中导入的文件名


# 去哪网的dao文件
#接收 base 文件  insertData传递过来的参数
def insertHotel(**kwargs):
    rs = None
    try:
        id = util.getUUID()
        sql = "insert into hotel(id,title,price) VALUES ('%s','%s','%s');" % (
            id, kwargs["title"], kwargs["price"])
        rs = dbmysql.query(sql)
    except Exception as e:
        util.logger.error(e)
    return rs