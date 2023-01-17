from flask import request, Blueprint, jsonify, render_template

from exts import db, basedir
from models.model import RepairServiceSheet
import os
import time
import xlwt as xlwt

repair = Blueprint('repair', __name__)


# 查询报修数据
@repair.route("/listView", methods=['GET', 'POST'])
def listView():
    return render_template('/repair/listView.html')


# 查询报修数据
@repair.route("/list", methods=['GET', 'POST'])
def list():
    page = request.args.get("page")
    limit = request.args.get("limit")
    status = request.args.get("status")
    applicantName = request.args.get("applicantName")
    dataw = None
    if applicantName is not None and applicantName != "" and status is not None and status != "":
        dataw = RepairServiceSheet.query.filter(RepairServiceSheet.applicantName == applicantName,
                                                RepairServiceSheet.status == status).order_by(
            RepairServiceSheet.id.desc()).paginate(int(page), per_page=int(limit), error_out=False)
    elif status is not None and status != "":
        dataw = RepairServiceSheet.query.filter(RepairServiceSheet.status == status).order_by(
            RepairServiceSheet.id.desc()).paginate(int(page), per_page=int(limit), error_out=False)
    elif applicantName is not None and applicantName != "":
        dataw = RepairServiceSheet.query.filter(
            RepairServiceSheet.applicantName == applicantName).order_by(
            RepairServiceSheet.id.desc()).paginate(int(page), per_page=int(limit), error_out=False)
    else:
        dataw = RepairServiceSheet.query.order_by(
            RepairServiceSheet.id.desc()).paginate(int(page), per_page=int(limit), error_out=False)
    jsonData = []
    for pet in dataw.items:
        repairDate = ''
        if pet.repairDate is not None:
            repairDate = pet.repairDate.strftime('%Y-%m-%d %Z %H:%M:%S')
        o = {"status": pet.status, "openid": pet.openid, 'id': pet.id, "address": pet.address,
             "description": pet.description,
             "applicantName": pet.applicantName, "remarks": pet.remarks, "mobile": pet.mobile, "type": pet.type,
             "imageUrl": pet.imageUrl, "radioUrl": pet.radioUrl, "repairDate": repairDate}
        jsonData.append(o)
    p = {'page': dataw.page, "data": jsonData, "count": dataw.total, "code": 0}
    return jsonify(p)


# 修改报修数据
@repair.route("/editView/<int:id>", methods=['GET', 'POST'])
def editView(id):
    return render_template('/repair/editView.html', id=id)


# 删除报修信息
@repair.route('/edit', methods=['POST'])
def edit():
    # 从request对象中读取表单内容：
    repairId = request.form['id']
    status = request.form['status']
    # 先查询再更新
    resultRepair = RepairServiceSheet.query.filter(RepairServiceSheet.id == repairId).first()
    resultRepair.status = status
    db.session.commit()
    print(resultRepair)
    if resultRepair.id > 0:
        return jsonify({'status': 200, 'errmsg': '修改成功！'})
    return jsonify({'status': 500, 'errmsg': '修改失败！'})


# 删除报修信息
@repair.route('/delete', methods=['POST'])
def delete():
    # 从request对象中读取表单内容：
    repairId = request.form['id']
    # 先查询再更新
    resultRepair = RepairServiceSheet.query.filter(RepairServiceSheet.id == repairId).first()
    db.session.delete(resultRepair)
    db.session.commit()
    print(resultRepair)
    if resultRepair.id > 0:
        return jsonify({'status': 200, 'errmsg': '删除成功！'})
    return jsonify({'status': 500, 'errmsg': '删除失败！'})


# 导出数据
@repair.route('exportData', methods=['POST'])
def exportData():
    wb = xlwt.Workbook()
    ws = wb.add_sheet('报修数据报表')
    first_col = ws.col(0)
    second_col = ws.col(1)
    third_col = ws.col(2)
    four_col = ws.col(3)
    five_col = ws.col(4)
    six_col = ws.col(5)
    first_col.width = 128 * 20
    second_col.width = 230 * 20
    third_col.width = 230 * 20
    four_col.width = 128 * 20
    five_col.width = 230 * 20
    six_col.width = 230 * 20
    ws.write(0, 0, "报修人")
    ws.write(0, 1, "联系电话")
    ws.write(0, 2, "报修地点")
    ws.write(0, 3, "报修描述")
    ws.write(0, 4, "报修备注")
    ws.write(0, 5, "报修状态")
    ws.write(0, 6, "报修时间")
    status = request.args.get("status")
    applicantName = request.args.get("applicantName")
    dataw = None
    if applicantName is not None and applicantName != "" and status is not None and status != "":
        dataw = RepairServiceSheet.query.filter(RepairServiceSheet.applicantName == applicantName,
                                                RepairServiceSheet.status == status).order_by(
            RepairServiceSheet.id.desc()).all()
    elif status is not None and status != "":
        dataw = RepairServiceSheet.query.filter(RepairServiceSheet.status == status).order_by(
            RepairServiceSheet.id.desc()).all()
    elif applicantName is not None and applicantName != "":
        dataw = RepairServiceSheet.query.filter(RepairServiceSheet.applicantName == applicantName).order_by(
            RepairServiceSheet.id.desc()).all()
    else:
        dataw = RepairServiceSheet.query.order_by(
            RepairServiceSheet.id.desc()).all()
    if dataw is not None:
        for i in range(0, len(dataw)):
            pet = dataw[i]
            repairDate = ''
            statusName = ''
            if pet.status == 1:
                statusName = "新报修"
            elif pet.status == 2:
                statusName = "维修中"
            elif pet.status == 3:
                statusName = "已完成"
            if pet.repairDate is not None:
                repairDate = pet.repairDate.strftime('%Y-%m-%d %Z %H:%M:%S')
            ws.write(i + 1, 0, pet.applicantName)
            ws.write(i + 1, 1, pet.mobile)
            ws.write(i + 1, 2, pet.address)
            ws.write(i + 1, 3, pet.description)
            ws.write(i + 1, 4, pet.remarks)
            ws.write(i + 1, 5, statusName)
            ws.write(i + 1, 6, repairDate)
    now = str(time.time())
    path = "/static/excel/"
    file_path = basedir + path
    fileName = "repair_" + now + ".xls"
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = file_path + fileName
    try:
        f = open(file_path, 'r')
        f.close()
    except IOError:
        f = open(file_path, 'w')
        f.close()
    wb.save(file_path)
    return path + fileName
