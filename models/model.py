from exts import db


# 用户模型
class User(db.Model):
    tableName = 'user'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    userName = db.Column(name='userName', nullable=False)
    userPassword = db.Column(db.String(30), nullable=False)
    openid = db.Column(name='openid', nullable=False)
    userType = db.Column(name='userType', nullable=False)


# 微信用户模型
class WxUser(db.Model):
    tableName = 'wx_user'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    openid = db.Column(name='openid', nullable=False)
    nickName = db.Column(name='nickName', nullable=False)
    avatarUrl = db.Column(name='avatarUrl', nullable=False)
    mobile = db.Column(name='mobile', nullable=False)
    realName = db.Column(name='realName', nullable=False)
    isBindingMobile = db.Column(name='isBindingMobile', nullable=False)


# 报修表模型
class RepairServiceSheet(db.Model):
    __tableName__ = 'repair_service_sheet'
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    openid = db.Column(name='openid', nullable=False)
    address = db.Column(name='address', nullable=False)
    description = db.Column(name='description', nullable=False)
    applicantName = db.Column(name='applicantName', nullable=False)
    remarks = db.Column(name='remarks', nullable=False)
    mobile = db.Column(name='mobile', nullable=False)
    type = db.Column(name='type', nullable=False)
    status = db.Column(name='status', nullable=False)
    imageUrl = db.Column(name='imageUrl', nullable=False)
    radioUrl = db.Column(name='radioUrl', nullable=False)
    repairDate = db.Column(name='repairDate', nullable=False)
