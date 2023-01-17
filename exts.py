import os

from flask_sqlalchemy import SQLAlchemy

# 此时先不传入app
db = SQLAlchemy()

# 项目根目录
basedir = os.path.abspath(os.path.dirname(__file__))

appId = "**"

appSecret = "**"



