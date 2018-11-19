#coding:utf-8
from . import api
from ihome.utils.commons import login_required
from flask import request, jsonify, current_app,session,g
from ihome.utils.response_code import RET
from ihome import redis_store, db,constants
from ihome.models import User,Area,House,Facility,HouseImage,User,Order
from ihome.utils.image_storage import storage
import json
from datetime import datetime

@api.route("/areas",methods=["GET"])
def get_area_info():
    """  获取城区信息"""
    #尝试从redis中读取数据
    try:
        resp_json = redis_store.get("area_info")  #下面保存数据库自己定义的
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json is not None:
            #redis有缓存数据，不走查询mysql数据库了
            # current_app.logger.info("hit redis area_info")  #往日志中写一份
            return resp_json,200,{"Content-Type":"application/json"}  #换成json格式的
    #查询数据库，读取城区信息
    try:
        area_li=Area.query.all()   #得到是个对象
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库异常")
    area_dict_li=[]
    #将对象转化为字典，aid aname 是自己定义的,每一次循环一组添加进去
    #还有一种方法是在models.py 文件写入方法
    for area in area_li:
        # d={
        #     "aid":area.id,
        #     "aname":area.name
        # }
        # area_dict_li.append(d)
        area_dict_li.append(area.to_dict())
    #将数据存储在redis内存式缓存数据库，读取速度更快，减轻mysql服务器压力
    resp_dict=dict(errno=RET.OK,errmsg="OK",data=area_dict_li)
    resp_json=json.dumps(resp_dict)  #将字典转换为字符串,保存在redis库中
    #将数据保存到redis中
    try:
        redis_store.setex("area_info",constants.AREA_INFO_REDIS_CACHE_EXPIRES,resp_json)
    except Exception as e:
        current_app.logger.error(e)
        #这也是一种格式，和jsonify 一样
    return resp_json, 200,{"Content-Type":"application/json"}

@api.route("/houses/info",methods=["POST"])
@login_required
def save_house_info():
    """  保存房屋的基本信息"""
    #获取数据
    user_id=g.user_id
    house_data=request.get_json()
    title=house_data.get("title")
    price=house_data.get("price")
    area_id=house_data.get("area_id")
    address=house_data.get("address")
    room_count=house_data.get("room_count")
    acreage=house_data.get("acreage") #房屋面积
    unit = house_data.get("unit")
    capacity=house_data.get("capacity") #房间容纳人数
    beds=house_data.get("beds")  #房屋卧床数目
    deposit=house_data.get("deposit")  #押金
    min_days=house_data.get("min_days")   #最小入住天数
    max_days=house_data.get("max_days")
    #校验参数
    if not all([title,price,area_id,address,room_count,acreage,unit,capacity,beds,deposit,min_days,max_days]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
    #判断金额是否正确
    try:
        #表中定义的字段为整型，需转化，而且存储为分，需乘以100
        price = int(float(price)*100)
        deposit=int(float(deposit)*100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    #判断城区id 是否存在
    try:
        area=Area.query.get(area_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if area is None:
        return jsonify(errno=RET.NODATA, errmsg="城区信息有误")

    #保存房屋信息,可查sqlcha语言保存进数据库格式
    house=House(
        user_id = user_id,
        area_id=area_id,
        title=title,
        price=price,
        address=address,
        room_count=room_count,
        acreage=acreage,
        unit=unit,
        capacity=capacity,
        beds=beds,
        deposit=deposit,
        min_days=min_days,
        max_days=max_days
    )
    #处理房屋的设施信息
    facility_ids=house_data.get("facility")
    #如果用户勾选了设施信息，再保存数据库
    if facility_ids:
        #["7","8"]
        try:
            #相当于  select * from ih_facility_info where id in []
            facilities=Facility.query.filter(Facility.id.in_(facility_ids)).all()
            print(facilities)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库异常")
        if facilities:
            #表示有合法的设施数据
            #保存设施数据
            house.facilities=facilities
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    #保存数据成功
    return jsonify(errno=RET.OK, errmsg="OK",data={"house_id":house.id})

@api.route("/houses/image",methods=["POST"])
@login_required
def save_house_image():
    """
    保存房屋的图片
    参数：图片 房屋的id
    """
    image_file=request.files.get("house_image") #得到表单上传图片的值
    house_id=request.form.get("house_id")  #得到表单中隐藏域（房屋的id）
    if not all([image_file,house_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    #判断house_id 正确性
    try:
        house=House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if house is None:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    #保存图片到七牛云
    image_data=image_file.read()
    try:
        file_name=storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="保存图片失败")
    #保存图片信息到数据库中
    house_image=HouseImage(house_id=house_id,url=file_name)
    db.session.add(house_image)
    #处理房屋的主图片（在轮播图中用）
    if not house.index_image_url:
        house.index_image_url=file_name
        db.session.add(house)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存图片数据异常")
    image_url=constants.QINIU_URL_DOMAIN + file_name
    return jsonify(errno=RET.OK, errmsg="OK",data={"image_url": image_url})

@api.route("/user/houses",methods=["GET"])
@login_required
def get_user_houses():
    """  获取房东发布的房源信息条目"""
    user_id = g.user_id
    try:
        user=User.query.get(user_id)
        houses=user.houses
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取数据失败")
    #将查询到的房屋信息转换为字典存放到列表中
    houses_list=[]
    if houses:
        for house in houses:
            houses_list.append(house.to_basic_dict())
    return jsonify(errno=RET.OK,errmsg="OK",data={"houses":houses_list})#传递给前端接收

@api.route("/houses/index",methods=["GET"])
def get_house_index():
    """  获取主页幻灯片展示的房屋基本信息"""
    #从缓存中尝试获取数据
    try:
        ret=redis_store.get("home_page_data") #自己定义的
    except Exception as e:
        current_app.logger.error(e)
        ret=None #有异常就让其为空
    if ret:
        current_app.logger.info("hit house index info redis")
        #因为redis中保存的是json字符串，所以，直接进行字符串拼接返回
        return '{"errno":0,"errmsg":"OK","data":%s}'% ret,200,{"Content-Type":"application/json"}
    else:
        try:
            #查询数据库，返回房屋订单数目最多的5条数据,按着订单数量降序
            houses=House.query.order_by(House.order_count.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="查询数据失败")
        if not houses:
            return jsonify(errno=RET.NODATA,errmsg="查询无数据")
        houses_list=[]
        for house in houses:
            #如果房屋未设置主图片，则跳过
            if not house.index_image_url:
                continue
            houses_list.append(house.to_basic_dict())
        #将数据转换为json字符串形式的，并保存到redis缓存
        json_houses=json.dumps(houses_list) #[{},{}]
        try:
            redis_store.setex("home_page_data",constants.HOME_PAGE_DATA_EXPIRES,json_houses)#房屋数据的redis缓存时间
        except Exception as e:
            current_app.logger.error(e)
        return '{"errno":0,"errmsg":"OK","data":%s}' % json_houses, 200, {"Content-Type": "application/json"}

@api.route("/houses/<int:house_id>",methods=["GET"])
def get_house_detail(house_id):
    """ 获取房屋信息"""
    #前端在房屋详情页面显示时，如果浏览器页面的用户不是该房屋的房东，则展示预订按钮，否则不展示
    #所以，需要后断返回登录用户的user_id
    #尝试获取用户登录的信息，若登录，则返回给前端登录用户的user_id,否则返回user_id=-1
    user_id=session.get("user_id","-1")
    #校验参数
    if not house_id:
        return jsonify(errno=RET.PARAMERR,errmsg="参数缺失")
    #从redis缓存中获取信息
    try:
        ret=redis_store.get("house_info_%s" % house_id)
    except Exception as e:
        current_app.logger.error(e)
        ret=None
    if ret:
        current_app.logger.info("hit house info redis")
        # 因为redis中保存的是json字符串，所以，直接进行字符串拼接返回
        return '{"errno":"0","errmsg":"OK","data":{"user_id":%s,"house":%s}}' % (user_id,ret), 200, {"Content-Type": "application/json"}
    try:
        # 查询数据库
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")
    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")
    #将房屋对象数据转换为字典
    try:
        house_data=house.to_full_dict()
        print("2222")
    except Exception as e:
        print("1111")
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据出错")
    # 将数据转换为json字符串形式的，并保存到redis缓存
    json_house = json.dumps(house_data)  # [{},{}]
    try:
        redis_store.setex("house_info_%s" % house_id, constants.HOUSE_DETAIL_EXPIRES, json_house)  # 房屋数据的redis缓存时间
    except Exception as e:
        current_app.logger.error(e)
    resp= '{"errno":"0","errmsg":"OK","data":{"user_id":%s,"house":%s}}' % (user_id,json_house), 200, {"Content-Type": "application/json"}
    return resp


# http://127.0.0.1:5000/search.html?aid=1&aname=东城区&sd=2018-10-18&ed=2018-10-19
@api.route("/houses")
def get_house_list():
    """  获取房屋的列表信息（搜索页面）"""
    start_date = request.args.get("sd","") #用户想要的起始时间
    end_date=request.args.get("ed","") #用户想要的结束时间
    area_id=request.args.get("aid","")#区域编号
    sort_key=request.args.get("sk","new") #排序关键字
    page=request.args.get("p") #页数

    try:
        if start_date:
            start_date=datetime.strptime(start_date,"%Y-%m-%d")
        if end_date:
            end_date=datetime.strptime(end_date,"%Y-%m-%d")
        if start_date and end_date:
            assert  start_date <= end_date #断言为真，true，否则出现异常
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg="日期参数有误")
    #判断区域id
    if area_id:
        try:
            area = Area.query.get(area_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="区域参数有误")
    #处理页面
    try:
        page=int(page) #转化为整型，如果不能转化，page=1
    except Exception as e:
        current_app.logger.error(e)
        page=1
    #获取redis缓存数据
    redis_key = "house_%s_%s_%s_%s" % (start_date, end_date, area_id, sort_key)
    try:
        resp_json=redis_store.hget(redis_key,page)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if resp_json:
            return resp_json, 200, {"Content-Type": "application/json"}


    #过滤条件的参数列表容器
    filter_params=[]
    #填充过滤参数
    #时间条件
    conflict_orders=None
    try:
        if start_date and end_date:
            #查询冲突的订单
            conflict_orders=Order.query.filter(Order.begin_date <= end_date,Order.end_date>=start_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(Order.end_date >= start_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(Order.begin_date <= end_date).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库异常")
    if conflict_orders:
        #从订单中获取冲突的房屋id
        conflict_orders_ids=[order.house_id for order in conflict_orders] #列表生成式
        #如果冲突的房屋id不为空，向查询参数中添加条件
        if conflict_orders_ids:
            filter_params.append(House.id.notin_(conflict_orders_ids)) #添加不是冲突的id
    #区域条件
    if area_id:
        filter_params.append(House.area_id == area_id)
    #排序条件
    if sort_key == "booking": #入住最多
        house_query=House.query.filter(*filter_params).order_by(House.order_count.desc()) #拆包降序
    elif sort_key == "price-inc": #价格 低-高
        house_query = House.query.filter(*filter_params).order_by(House.price.asc())
    elif sort_key == "price-des": #价格 高-低
        house_query = House.query.filter(*filter_params).order_by(House.price.desc)
    else:  #最新上线的话，按添加时间降序
        house_query = House.query.filter(*filter_params).order_by(House.create_time.desc())
    try:
        #处理分页                       当前页数           每页数据量                         自动错误输出
        page_obj = house_query.paginate(page=page,per_page=constants.HOUSE_LIST_PAGE_CAPACITY,error_out=False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")

    #获取页面数据
    house_li = page_obj.items
    houses=[]
    for house in house_li:
        houses.append(house.to_basic_dict())
    #获取总页数
    total_page=page_obj.pages
    #设置缓存数据
    resp_dict = dict(errno=RET.OK,errmsg="OK",data={"total_page":total_page,"houses":houses,"current_page":page})
    resp_json = json.dumps(resp_dict)
    if page <= total_page:
        redis_key = "house_%s_%s_%s_%s" %(start_date,end_date,area_id,sort_key)
        #哈希类型
        try:
            redis_store.hset(redis_key,page,resp_json)
            redis_store.expire(redis_key,constants.HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES)
        except Exception as e :
            current_app.logger.error(e)
    return resp_json,200,{"Content-Type":"application/json"}


