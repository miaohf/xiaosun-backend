from datetime import datetime
import math
from app.models import Role, User, Equipment, Action, City, EquipmentType, ActionType
from sqlalchemy import func
from app import create_app, db
app = create_app()
app.app_context().push()


cities = ['溧阳', '上海', '苏州', '杭州']
equipment_type_items = ['平刨', '压刨', '带锯', '台锯', '多功能工作台']

for c in cities:
    city = City(name=c)
    db.session.add(city)
db.session.commit()

for n in equipment_type_items:
    type = EquipmentType(name=n)
    db.session.add(type)
db.session.commit()


equipments = [
    ['生产一厂', 'V1T20190623', 'abcd01349901', '设备a001', 1, 1, 1, 1],
    ['生产一厂', 'V2T20200623', 'afcd01349902', '设备a002', 0, 2, 2, 1],
    ['生产一厂', 'V2T20200623', 'adsf01349903', '设备a003', 9, 3, 3, 1],
    ['生产一厂', 'V2T20200623', 'agfd01349904', '设备a004', 9, 4, 4, 1],
    ['生产一厂', 'V2T20200623', 'afgd01349905', '设备a005', 0, 1, 1, 1],
    ['生产一厂', 'V3T20200311', 'afgd01349906', '设备a006', 0, 2, 2, 1],
    ['杭州一厂', 'V4T20221017', 'cbcd01349901', '设备c001', 1, 3, 3, 1],
    ['杭州一厂', 'V4T20221017', 'cfcd01349902', '设备c002', 0, 4, 4, 0],
    ['杭州一厂', 'V4T20221017', 'cdsf01349903', '设备c003', 9, 1, 1, 0],
    ['杭州一厂', 'V4T20221017', 'cgfd01349904', '设备c004', 9, 2, 2, 0],
    ['杭州一厂', 'V6T20220901', 'cfgd01349905', '设备c005', 0, 3, 3, 0],
    ['杭州一厂', 'V6T20220901', 'cfgd01349906', '设备c006', 0, 4, 4, 0],
    ['溧阳二厂', 'V6T20220901', 'hbcd01349931', '设备h001', 1, 1, 1, 0],
    ['溧阳二厂', 'V6T20220901', 'hfcd01349932', '设备h002', 0, 2, 2, 0],
    ['溧阳二厂', 'V6T20220901', 'hdsf01349933', '设备h003', 9, 3, 3, 0],
    ['溧阳二厂', 'V6T20220901', 'hgfd01349934', '设备h004', 9, 4, 4, 0],
    ['溧阳二厂', 'V6T20220901', 'hfgd01349935', '设备h005', 0, 1, 1, 0],
    ['溧阳二厂', 'V6T20220901', 'hfgd01349936', '设备h006', 0, 2, 2, 0],
]

[
    # ['制作-格角榫', 1, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-托角榫', 2, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-粽角榫', 3, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-燕尾榫', 4, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-夹头榫', 5, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-抱肩榫', 6, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-龙凤榫', 7, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-楔钉榫', 8, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-插肩榫', 10, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-围栏榫', 13, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-套榫', 11, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-挂榫', 12, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-半榫', 15, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
    # ['制作-札榫', 16, 1, 1, 20, 10, 60, 10, 5, 120, 2, 1, 3],
]


for ep in equipments:
    equipment = Equipment(
        node_name=ep[0],
        version=ep[1],
        equipment_code=ep[2],
        name=ep[3],
        status=ep[4],
        city_id=ep[5],
        type_id=ep[6],
        is_online=ep[7],
    )
    db.session.add(equipment)

db.session.commit()


# assembly_type: 0 单排， 1 双排， 2 复合
action_type_items = [
    ['榫头', '1001', 0, 0],
    ['榫眼', '1002', 1, 0],
    ['单排榫头', '2001', 0, 0],
    ['单排榫眼', '2002', 1, 0],
    ['竖排榫头', '3001', 0, 1],
    ['竖排榫眼', '3002', 1, 1],
    ['四榫头', '4001', 0, 1],
    ['四榫眼', '4002', 1, 1],
    ['复合榫头', '5001', 0, 2],
    ['复合榫眼', '5002', 1, 2],
    ['燕尾拼榫', '6000', 9, 0],
    ['直拼榫', '7000', 9, 0],
    ['抄手榫', '8000', 9, 0],
]

for ati in action_type_items:
    actiontype = ActionType(
        name=ati[0],
        action_code=ati[1],
        is_mortise=ati[2],
        assembly_type=ati[3]
    )
    db.session.add(actiontype)

db.session.commit()

r1 = Role(name='admin', authority='administrator')
db.session.add(r1)


# admin
u2 = User(username='admin', fullname='管理员',
          mail='admin@xiaosun.co', company='小隼制造')
u2.set_password('12345678')
r1.users.append(u2)

u2 = User(username='zhangzy', fullname='章正一',
          mail='zhangzy@xiaosun.co', company='小隼制造')
u2.set_password('12345678')
r1.users.append(u2)

u3 = User(username='ranwy', fullname='冉维尧',
          mail='ranwy@xiaosun.co', company='小隼制造')
u3.set_password('12345678')
r1.users.append(u3)

u1 = User(username='miaohf', fullname='缪海锋',
          mail='miaohf@xiaosun.co', company='小隼制造')
u1.set_password('12345678')
r1.users.append(u1)

u4 = User(username='zhangsan', fullname='张三',
          mail='zhangsan@xiaosun.co', company='小隼制造', status=0)
u4.set_password('12345678')
r1.users.append(u4)

db.session.commit()


equipments = Equipment.query.all()
users = User.query.all()

for u in users:
    for em in equipments:
        u.equipments.append(em)

db.session.commit()
