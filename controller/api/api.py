import hashlib
import json


import uuid
from datetime import datetime

import requests
from PIL import Image
from flask import Blueprint, jsonify, request, session

from exts import db, basedir, appId, appSecret
from models.model import RepairServiceSheet, WxUser, User

api = Blueprint('api', __name__)


# 用户登录接口
@api.route('/signIn', methods=['POST'])
def signIn():
    # 从request对象中读取表单内容：
    username = request.form.get('username')
    password = request.form['password']
    userResult = User.query.filter(User.userName == username).first()  # 简单查询  使用关键字实参的形式来设置字段名
    if userResult is not None:
        a = hashlib.md5()
        a.update(password.encode(encoding="utf-8"))
        md5Password = a.hexdigest()  # sha1哈希加密
        if md5Password == userResult.userPassword:
            session['username'] = userResult.userName
            return jsonify({'status': 200, 'errmsg': '登录成功！'})
        return jsonify({'status': 500, 'errmsg': '用户密码错误，请输入正确的密码！'})
    return jsonify({'status': 500, 'errmsg': '登录失败，用户不存在！'})


# 上传图片
@api.route('/v1/upload', methods=['post'])
def up_photo():
    img = request.files.get('file')
    fileName = str(uuid.uuid1())
    print(fileName)
    img = Image.open(img)
    img_w, img_h = img.size
    set_size(img, img_w, img_h, 1, basedir + '/static/images/', fileName + '_L', '.png')
    imgL = fileName + '_L.png'
    path = "/static/images/" + imgL
    return jsonify({'status': 200, 'url': path})


# 保存图片到本地
def set_size(im, width, height, size, path, name, Suffix):
    img_w, img_h = int(width * size), int(height * size)
    img = im.resize((img_w, img_h), Image.ANTIALIAS)
    imgPath = path + name + Suffix
    img.save(imgPath, quality=70, subsampling=0)


# 用户绑定
@api.route('v1/user/binding', methods=['POST'])
def binding():
    realName = request.form.get("realName")
    mobile = request.form.get("mobile")
    userId = request.form.get("userId")
    wxUser = WxUser.query.filter(WxUser.id == userId).first()
    wxUser.realName = realName
    wxUser.mobile = mobile
    wxUser.isBindingMobile = 1
    db.session.commit()
    return jsonify({'status': 200, 'errmsg': '绑定成功！'})


# 添加报修信息
@api.route('/v1/repair/add', methods=['POST'])
def repairAdd():
    # 从request对象中读取表单内容：
    address = request.form['address']
    description = request.form['description']
    applicantName = request.form['applicantName']
    remarks = request.form['remarks']
    mobile = request.form['mobile']
    _type = request.form['type']
    imageUrl = request.form['imageUrl']
    openid = request.form['openid']
    radioUrl = request.form['radioUrl']
    param = RepairServiceSheet(status=1,address=address, description=description, applicantName=applicantName, remarks=remarks,
                               mobile=mobile, type=_type, imageUrl=imageUrl, openid=openid, radioUrl=radioUrl,
                               repairDate=datetime.now())
    db.session.add(param)
    db.session.commit()
    if param.id > 0:
        return jsonify({'status': 200, 'errmsg': '添加成功！'})
    return jsonify({'status': 500, 'errmsg': '添加失败！'})


# 查询报修信息数据返回json
@api.route("/v1/repair/list/<int:page>/<int:per_page>", methods=['GET', 'POST'])
def repairList(page, per_page):
    openid = request.args.get("openid")
    status = request.args.get("status")
    dataw = RepairServiceSheet.query.filter(RepairServiceSheet.openid == openid,RepairServiceSheet.status == status).order_by(
        RepairServiceSheet.id.desc()).paginate(page, per_page=per_page, error_out=False)
    jsonData = []
    for pet in dataw.items:
        repairDate = ''
        if pet.repairDate is not None:
            repairDate = pet.repairDate.strftime('%Y-%m-%d %Z %H:%M:%S')
        o = {'openid': pet.openid, 'id': pet.id, "address": pet.address, "description": pet.description,
             "applicantName": pet.applicantName, "remarks": pet.remarks, "mobile": pet.mobile, "type": pet.type,
             "imageUrl": pet.imageUrl, "radioUrl": pet.radioUrl, "repairDate": repairDate}
        jsonData.append(o)
    p = {'page': dataw.page, "list": jsonData}
    return jsonify(p)


# 请求微信接口获取openid、session_key
@api.route("/v1/wx/login", methods=['GET', 'POST'])
def wxLogin():
    code = request.args.get("code")
    wxUrl = "https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={appSecret}&js_code={code}&grant_type=authorization_code".format(
        appId=appId, appSecret=appSecret, code=code)
    req = requests.get(wxUrl)  # wxUrl 你要请求的接口地址
    jsonText = req.text  # wxUrl接口地址返回的数据字符串
    resultJson = json.loads(jsonText)  # 将json字符串转换成字典
    resultUser = WxUser.query.filter(WxUser.openid == resultJson['openid']).first()
    if resultUser is not None:
        jsonData = {'id': resultUser.id, 'openid': resultUser.openid, "avatarUrl": resultUser.avatarUrl,
                    "nickName": resultUser.nickName,
                    "isBindingMobile": resultUser.isBindingMobile, "mobile": resultUser.mobile,
                    "realName": resultUser.realName}
        resultJson = jsonData
    else:
        resultJson = {"openid": resultJson['openid']}
    return resultJson


# 通过 openid 获取用户信息
@api.route("/v1/wx/getUserInfoByOpenid", methods=['GET', 'POST'])
def wxGetUserInfoByOpenid():
    openid = request.args.get("openid")
    print(openid)
    resultUser = WxUser.query.filter(WxUser.openid == openid).first()
    print(resultUser)
    if resultUser is not None:
        jsonData = {'id': resultUser.id, 'openid': resultUser.openid, "avatarUrl": resultUser.avatarUrl,
                    "nickName": resultUser.nickName,
                    "isBindingMobile": resultUser.isBindingMobile}
        resultJson = {"code": 200, "obj": jsonData}
    else:
        resultJson = {"code": 500, "obj": ''}
    return resultJson


# 保存微信用户信息
@api.route("/v1/wx/saveUserInfo", methods=['GET', 'POST'])
def saveUserInfo():
    openid = request.args.get("openid")
    nickName = request.args.get("nickName")
    avatarUrl = request.args.get("avatarUrl")
    param = WxUser(nickName=nickName, openid=openid, avatarUrl=avatarUrl)
    db.session.add(param)
    db.session.commit()
    if param.id > 0:
        return jsonify({'status': 200, 'errmsg': '添加成功！'})
    return jsonify({'status': 500, 'errmsg': '添加失败！'})


