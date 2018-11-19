from flask import Flask, render_template, request, jsonify
from flask import jsonify
from dao import flaskdao

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

#页面显示内容的
@app.route('/list')
def list():
    rs = flaskdao.getDataAll()
    return render_template('list.html', rs=rs)

#显示详情页的
@app.route('/detail/<ggId>')
def detail(ggId):
    rs = flaskdao.getDataById(ggId)
    return render_template('detail.html', rs=rs)

#推送给web数据库的接口
@app.route('/chaxun/v1', methods=['POST'])
def reject():
    ret = {}
    ret["retCode"] = "0001"
    ret["retMsg"] = "您的网络开小差了"
    title = request.form['title']
    body = request.form['body']
    times = request.form['times']
    flaskdao.insertgonggao(title=title, body=body, times=times,url='123')
    ret["retCode"] = "0000"
    ret["retMsg"] = "插入成功"
    return jsonify(ret)


if __name__ == '__main__':
    app.run()
