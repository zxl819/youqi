import os

from flask import Flask, request, redirect, session, render_template

import config
from controller.api.api import api
from controller.repair.repair import repair
from controller.user.user import user
from exts import db

app = Flask(__name__)
app.config['REDIS_HOST'] = "127.0.0.1"  # redis数据库地址
app.config['REDIS_PORT'] = 6379  # redis 端口号
app.config['REDIS_DB'] = 0  # 数据库名
app.config['REDIS_EXPIRE'] = 60  # redis 过期时间60秒
app.config.from_object(config)
db.init_app(app)

# 注册user，使用前缀 user 作为前缀访问
app.register_blueprint(user, url_prefix='/user')
# 注册api，使用前缀 api 作为前缀访问
app.register_blueprint(api, url_prefix='/api')
# 注册repair，使用前缀 repair 作为前缀访问
app.register_blueprint(repair, url_prefix='/repair')

# 设置编码
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = os.urandom(24)


# 用户登录view
@app.route('/login')
def login():
    return render_template("/login.html")


# 退出登录view
@app.route('/logout')
def logout():
    del session['username']
    return render_template("/login.html")


# 后台主页view
@app.route('/home')
def home():
    return render_template('/home.html', userName=session.get("username"))


# 请求拦截器，对未登录的链接进行拦截，防止非法访问
@app.before_request
def before_user():
    if request.path == "/login":
        return None
    if request.path.startswith("/static"):
        return None
    if request.path.startswith("/api"):
        return None
    if not session.get("username"):
        return redirect("/login")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090)
