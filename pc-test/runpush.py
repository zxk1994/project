import requests
from dao import gonggaodao
import json,time

if __name__ == '__main__':
    while 1:
        rs = gonggaodao.getDataAll()
        for item in rs:
            data = {"title": item.title, "body": item.body, "times": item.times}
            r = requests.post("http://127.0.0.1:5000/chaxun/v1", data=data)
            r2 = json.loads(r.content.decode())
            print(r2)
        time.sleep(1)
