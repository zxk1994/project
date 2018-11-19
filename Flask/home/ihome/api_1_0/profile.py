#coding:utf-8

from . import api
from ihome.utils.commons import login_required  #验证登录
from flask import request, jsonify, current_app,g,session
from ihome.utils.response_code import RET
from ihome.models import User
from ihome import db,constants
from ihome.utils.image_storage import storage

#设置用户的头像
@api.route("/users/avatar",methods=["POST"])
@login_required
def set_user_avatar():
    """
    设置用户的头像
    参数：图片 用户id(g.user_id)
    :return:
    """
    #装饰器的代码中已经将user_id保存到g全局对象中，所以试图可以直接读取
    user_id=g.user_id
    #对于上传的文件都要用files，其余的都要用args
    image_file=request.files.get("avatar")  #需要前端name定义这个名字
    if image_file is None:
        return jsonify(errno=RET.PARAMERR,errmsg="未上传图片")
    #读取二进制的数据，如果是put_file形式的就不用了
    image_data=image_file.read()
    #调用七牛云上传图片
    try:
        # 调用这个上传图片的方法,得到保存的图片的文件名
        file_name=storage(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片失败")
    #保存文件名到数据库
    try:
        #查询对应的id 更新avatar_url字段，没有添加字段， 存在，更新
        User.query.filter_by(id=user_id).update({"avatar_url":file_name})
        db.session.commit()  #提交保存
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片信息失败")
    #保存成功以后，将图片的完整路径返回给前端,拼接路径字符串
    avatar_url=constants.QINIU_URL_DOMAIN+ file_name
    return jsonify(errno=RET.OK, errmsg="保存成功", data={"avatar_url":avatar_url})


@api.route("/users/name",methods=["PUT"])
@login_required
def change_user_name():
    """  修改用户名 """
    #使用了login_required装饰器后，可以从g全局对象中获取user_id 对象
    user_id=g.user_id
    #设置用户想要设置的用户名
    req_data=request.get_json()  #得到json格式的
    if not req_data:
        return jsonify(errno=RET.PARAMERR,errmsg="参数不完整")
    name=req_data.get("name")  #拿到输入框中输入的名字，前端的name必须叫name
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="名字不能为空")
    #保存用户昵称name，判断name是否重复（利用数据库的唯一索引 unique=True 唯一）
    try:
        User.query.filter_by(id=user_id).update({"name":name})  #查询更新名字
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="设置用户错误")
    #更新session会话机制的内容,使页面右上角的手机号换成名字
    session["name"]=name
    return jsonify(errno=RET.OK,errmsg="OK",data={"name":name})

@api.route("/user",methods=["GET"])
@login_required
def get_user_profile():
    """ 获取个人信息,一开始页面会显示信息 """
    user_id=g.user_id
    #查询数据库查询数据
    try:
        user=User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户信息失败")
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")
    #把modles.py 中的to_dic() 函数转化，传参,或下面这个格式转化
    # user={
    #     "user":user.name,
    #     "mobile":user.mobile
    # }
    return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())


@api.route("/users/auth",methods=["GET"])
@login_required
def get_user_auth():
    """ 获取用户的实名认证信息，一开始页面会显示信息 """
    user_id=g.user_id
    #查询数据库查询数据
    try:
        user=User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取用户实名认证信息失败")
    if user is None:
        return jsonify(errno=RET.NODATA, errmsg="无效操作")
    #把modles.py 中的auth_to_dic() 函数转化，传参,或下面这个格式转化

    return jsonify(errno=RET.OK, errmsg="OK", data=user.auth_to_dict())


@api.route("/users/auth",methods=["POST"])
@login_required
def set_user_auth():
    """ 保存实名认证信息"""
    user_id=g.user_id
    #1、获取参数
    req_data=request.get_json()
    if not req_data:
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    #前端的名字name=必须也是real_name id_card
    real_name=req_data.get("real_name") #真实姓名
    id_card=req_data.get("id_card")  #身份证号
    #2、进行校验
    if not all([real_name,id_card]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    #把真实姓名和身份证号保存到数据库中
    #real_name=None,id_card=None，必须为空才能认证
    try:
        User.query.filter_by(id=user_id,real_name=None,id_card=None).update({"real_name":real_name,"id_card":id_card})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="保存用户实名信息失败")
    return jsonify(errno=RET.OK, errmsg="保存成功")


