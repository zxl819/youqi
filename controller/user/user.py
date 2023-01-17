import hashlib

from flask import request, Blueprint, jsonify, render_template

from exts import db
from models.model import User

user = Blueprint('user', __name__)


# 用户添加view
@user.route('/addView')
def addView():
    return render_template('/user/addView.html')


# 用户修改view
@user.route('/editView')
def editView():
    userId = request.args["userId"]
    resultUser = User.query.filter(User.id == userId).first()
    return render_template('/user/editView.html', info=resultUser)


# 查询用户数据
@user.route("/listView/<int:page>", methods=['GET', 'POST'])
def listView(page=1):
    users = User.query.order_by(User.id.desc()).paginate(page, per_page=10)
    return render_template('/user/listView.html', infos=users.items, pagination=users)


# 添加用户信息
@user.route('/add', methods=['POST'])
def add():
    # 从request对象中读取表单内容：
    userName = request.form['userName']
    password = request.form['password']
    print("userName=" + userName)
    print("password=" + password)
    a = hashlib.md5()
    a.update(password.encode(encoding="utf-8"))
    md5Password = a.hexdigest()  # sha1哈希加密
    param = User(userName=userName, userPassword=md5Password)
    db.session.add(param)
    db.session.commit()
    if param.id > 0:
        return jsonify({'status': 200, 'errmsg': '添加成功！'})
    return jsonify({'status': 500, 'errmsg': '添加失败！'})


# 修改用户信息
@user.route('/edit', methods=['POST'])
def edit():
    # 从request对象中读取表单内容：
    password = request.form['password']
    userId = request.form['id']
    # 先查询再更新
    resultUser = User.query.filter(User.id == userId).first()
    a = hashlib.md5()
    a.update(password.encode(encoding="utf-8"))
    md5Password = a.hexdigest()  # sha1哈希加密
    print("oldPassword=" + resultUser.userPassword)
    print("password=" + password)
    resultUser.userPassword = md5Password
    db.session.commit()
    print(resultUser)
    if resultUser.id > 0:
        return jsonify({'status': 200, 'errmsg': '修改成功！'})
    return jsonify({'status': 500, 'errmsg': '修改失败！'})


# 删除用户信息
@user.route('/delete', methods=['POST'])
def delete():
    # 从request对象中读取表单内容：
    userId = request.form['id']
    # 先查询再更新
    resultUser = User.query.filter(User.id == userId).first()
    db.session.delete(resultUser)
    db.session.commit()
    print(resultUser)
    if resultUser.id > 0:
        return jsonify({'status': 200, 'errmsg': '删除成功！'})
    return jsonify({'status': 500, 'errmsg': '删除失败！'})
