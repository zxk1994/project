#coding:utf-8
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from ihome import constants
from . import db

#create_time 字段数据首次插入的时间
#update_time 字段数据更新的时间  #onupdate 表示在数据发生改动的时候，调用onupdate

class BaseModel(object):
    # 模型抽象基类,为每个模型补充创建时间和更新时间
    create_time=db.Column(db.DateTime,default=datetime.now)  #记录的创建时间
    update_time =db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)#记录的更新时间  #记录的创建时间

class User(BaseModel,db.Model):
    """  用户 """
    __tablename__ = "ih_user_profile"

    id=db.Column(db.Integer,primary_key=True) #用户编号
    name=db.Column(db.String(32),unique=True,nullable=False)#用户昵称
    mobile=db.Column(db.String(11),unique=True,nullable=False)#手机号
    password_hash=db.Column(db.String(128),nullable=False) #加密的密码
    real_name =db.Column(db.String(32))#真实姓名
    id_card=db.Column(db.String(20),unique=True)  #身份证号
    avatar_url=db.Column(db.String(128))#用户头像路径

    houses=db.relationship("House",backref="user") #用户发布的房屋
    orders=db.relationship("Order",backref="user") #用户下的订单

    #password.setter 这个password和上面的属性名一致
    @property
    def password(self):
        """  获取password属性时被调用"""
        raise AttributeError("not readable 不可读")
    @password.setter
    def password(self,password):
        """  设置password 属性时被调用 设置密码加密"""
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        """  检查密码的正确性，数据库密码，用户填写的密码等传参"""
        return check_password_hash(self.password_hash,password)

    def to_dict(self):
        """  将对象转换为字典数据"""
        user_dict={
            "user_id":self.id,
            "name":self.name,
            "mobile":self.mobile,
            "avatar":constants.QINIU_URL_DOMAIN+self.avatar_url if self.avatar_url else "", #列表判断格式，如果就执行，否则为空
            "create_time":self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return user_dict

    def auth_to_dict(self):
        """  将实名信息转换为字典数据"""
        auth_dict={
            "user_id":self.id,
            "real_name":self.real_name,
            "id_card":self.id_card
        }
        return auth_dict

class Area(BaseModel,db.Model):
    """  城区"""
    __tablename__ = "ih_area_info"

    id=db.Column(db.Integer,primary_key=True) #区域编号
    name=db.Column(db.String(32),nullable=False) #区域名字
    houses=db.relationship("House",backref="area") #区域的房屋

    def to_dict(self):
        """  将对象转换为字典数据"""
        area_dict={
            "aid":self.id,
            "aname":self.name
        }
        return area_dict


#房屋设施表，建立房屋与设施的多对多关系  中间表链接设施和房屋的
house_facility=db.Table(
    "ih_house_facility",
    db.Column("house_id",db.Integer,db.ForeignKey("ih_house_info.id"),primary_key=True),#房屋编号
    db.Column("facility_id",db.Integer,db.ForeignKey("ih_facility_info.id"),primary_key=True)#设施编号
)

class House(BaseModel,db.Model):
    """ 房屋信息"""
    __tablename__="ih_house_info"

    id=db.Column(db.Integer,primary_key=True) #房屋编号
    user_id=db.Column(db.Integer,db.ForeignKey("ih_user_profile.id"),nullable=False)#房屋主人的用户
    area_id =db.Column(db.Integer,db.ForeignKey("ih_area_info.id"),nullable=False)#归属地的区域编号
    title=db.Column(db.String(64),nullable=False)#标题
    price=db.Column(db.Integer,default=0) #单价，单位：分
    address=db.Column(db.String(512),default="")#地址
    unit=db.Column(db.String(32),default="")#房屋单元，如几室几厅
    room_count=db.Column(db.Integer,default=1) #房间数目
    acreage=db.Column(db.Integer,default=0) #房屋面积
    capacity = db.Column(db.Integer, default=1)  # 房屋容纳的人数
    beds = db.Column(db.String(64), default="")  # 房屋床铺的配置
    deposit = db.Column(db.Integer, default=0)  # 房屋押金
    min_days = db.Column(db.Integer, default=1)  # 最少入住天数
    max_days = db.Column(db.Integer, default=0)  # 最多入住天数，0表示不限制
    index_image_url = db.Column(db.String(256), default="")  # 房屋主图片的路径
    order_count = db.Column(db.Integer, default=0)  # 预订完成的该房屋的订单数
    image=db.relationship("HouseImage") #房屋的图片
    facilities=db.relationship("Facility",secondary=house_facility)#房屋的设施
    orders=db.relationship("Order",backref="house")#房屋的订单


    def to_full_dict(self):
        house_dict = {
            'hid': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name,
            'user_avatar': constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            'title': self.title,
            'price': self.price,
            'address': self.address,
            'room_count': self.room_count,
            'acreage': self.acreage,
            'unit': self.unit,
            'capacity': self.capacity,
            'beds': self.beds,
            'deposit': self.deposit,
            'min_days': self.min_days,
            'max_days': self.max_days
        }
        # 房屋图片
        img_urls = []
        for image in self.image:
            img_urls.append(constants.QINIU_URL_DOMAIN + image.url)
        house_dict['img_urls'] = img_urls
        # 房屋设施
        facilities = []
        for facility in self.facilities:
            facilities.append(facility.id)
        house_dict['facilities'] = facilities

        #评论信息
        comments = []
        orders = Order.query.filter(Order.house_id ==self.id,Order.status == "COMPLETE",Order.comment != None).order_by(
            Order.update_time.desc()).limit(constants.HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS)
        for order in orders:
             comment ={
                 "comment":order.comment,
                 "user_name":order.user.name if order.user.name != order.user.mobile else "匿名用户" ,#发表评论的用户
                 "ctime": order.update_time.strftime("%Y-%m-%d %H:%M:%S") #评价的时间
             }
             comments.append(comment)
        house_dict["comments"] = comments
        return house_dict


    def to_basic_dict(self):
        house_dict={
            "house_id":self.id,
            "title":self.title,
            "price":self.price,
            "area_name":self.area.name,
            "img_url":constants.QINIU_URL_DOMAIN+self.index_image_url if self.index_image_url else "",
            "room_count":self.room_count,
            "order_count":self.order_count,
            "address":self.address,
            "user_avatar": constants.QINIU_URL_DOMAIN + self.user.avatar_url if self.user.avatar_url else "",
            "ctime":self.create_time.strftime("%Y-%m-%d")
        }
        return  house_dict

class Facility(BaseModel,db.Model):
    """   设施信息  """
    __tablename__ = "ih_facility_info"

    id = db.Column(db.Integer,primary_key=True) #设置编号
    name = db.Column(db.String(32),nullable=False) #设施名字

class HouseImage(BaseModel,db.Model):
    """   房屋图片  """
    __tablename__ = "ih_house_image"

    id = db.Column(db.Integer,primary_key=True)
    house_id = db.Column(db.Integer,db.ForeignKey("ih_house_info.id"),nullable=False) #房屋编号
    url = db.Column(db.String(256),nullable=False) #图片路径

class Order(BaseModel,db.Model):
    """   订单  """
    __tablename__ = "ih_order_info"

    id = db.Column(db.Integer,primary_key=True) #订单编号

    user_id = db.Column(db.Integer,db.ForeignKey("ih_user_profile.id"),nullable=False) #下订单的用户编号
    house_id = db.Column(db.Integer,db.ForeignKey("ih_house_info.id"),nullable=False) #预订的房间编号

    begin_date = db.Column(db.DateTime,nullable=False) #预定的起始时间
    end_date = db.Column(db.DateTime,nullable=False) #预定结束时间
    days = db.Column(db.Integer,nullable=False) #预定的总天数
    house_price = db.Column(db.Integer,nullable= False) #房屋的单价
    amount = db.Column(db.Integer,nullable=False) #订单的总金额
    status = db.Column(db.Enum(#订单的状态
        "WAIT_ACCEPT",#待接单
        "WAIT_PAYMENT", #待支付
        "PAID", #已支付
        "WAIT_COMMENT", #待评价
        "COMPLETE",#已完成
        "CANCELED", #已取消
        "REJECTED" #已拒单
    ),default="WAIT_ACCEPT",index = True) #index为字段添加索引，提高查询效率
    comment = db.Column(db.Text) #订单的评论信息或者拒单原因
    trade_no = db.Column(db.String(128)) #支付交易编号

    def to_dict(self):
        """   将订单信息转换为字段数据  """
        order_dict ={
            "order_id":self.id,
            "title":self.house.title,
            "img_url":constants.QINIU_URL_DOMAIN + self.house.index_image_url if self.house.index_image_url else"",
            "start_date": self.begin_date.strftime("%Y-%m-%d"),
            "end_date":self.end_date.strftime("%Y-%m-%d"),
            "ctime":self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "days":self.days,
            "amount":self.amount,
            "status":self.status,
            "comment":self.comment if self.comment else"" #评论字段还么添加呢

        }
        return order_dict






