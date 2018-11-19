#coding:utf-8

from ihome import create_app,db
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app=create_app("develop")  #传参（"develop" "product"）
#让Python支持命令行工作
manager=Manager(app)
#使用migrate 绑定app和db
migrate=Migrate(app,db)
#添加迁移脚本的命令到manager中
manager.add_command('db',MigrateCommand)

#启动项目
if __name__=="__main__":
    manager.run()