from datetime import datetime, timedelta
from hashlib import md5
import json
import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, current_app, g, jsonify
from app import db
from sqlalchemy.inspection import inspect

from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method

# from dateutil import parser
from app.utils import getdatetime

from sqlalchemy import DECIMAL, UniqueConstraint

# from sqlalchemy import event, DDL

# import sys

# sys.setrecursionlimit(34)


users_roles = db.Table(
    'users_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.PrimaryKeyConstraint('user_id', 'role_id'),
)


users_equipments = db.Table(
    'users_equipments',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('equipment_id', db.Integer, db.ForeignKey('equipments.id')),
    db.PrimaryKeyConstraint('user_id', 'equipment_id'),
)


class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    # @staticmethod
    # def serialize_list(l):
    #     return [m.serialize() for m in l]


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, **kwargs):
        resources = query.paginate(
            page=page, per_page=per_page, error_out=False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
        }
        return data

    def to_collection_dict_for_list(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(
            page=page, per_page=per_page, error_out=False)
        data = {
            'items': [item.to_dict_for_list() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, Serializer, db.Model):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    username = db.Column(db.String(64))
    company = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))  # 不保存原始密码
    fullname = db.Column(db.String(64))
    avatarurl = db.Column(db.String(64))
    company = db.Column(db.String(64))
    mail = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    status = db.Column(db.Integer, default=1)  # 状态 0初始, 1正常
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    login_counts = db.Column(db.Integer, default=0)

    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic', cascade='all, delete-orphan')

    actions = db.relationship('Action', backref='user', lazy='dynamic')
    jobs = db.relationship('Job', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        '''头像'''
        if self.email:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            avatar = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
                digest, size)
        else:
            avatar = None
        return avatar

    @classmethod
    def dinamic_filter(model_class, filter_condition):
        __query = db.session.query(model_class)
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception('Invalid filter: %s' % raw)
            column = getattr(model_class, key, None)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                try:
                    attr = list(filter(lambda e: hasattr(column, e %
                                op), ['%s', '%s_', '__%s__']))[0] % op
                except IndexError:
                    raise Exception('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            __query = __query.filter(filt)
        return __query

    @staticmethod
    def serialize_list_for_role(l):
        return [m.authority for m in l]

    @staticmethod
    def serialize_list(l):
        return [m.to_dict() for m in l]

    @staticmethod
    def get_role_name(l):
        return [r.name for r in l]

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'fullname': self.fullname,
            'mail': self.mail,
            'company': self.company,
            'role_name': self.get_role_name(self.roles),
            'login_counts': self.login_counts,
            'role': self.roles[0].name,
            'roles': self.serialize_list_for_role(self.roles),
            'location': self.location,
            'about_me': self.about_me,
            'status': self.status,
            'member_since': self.member_since.isoformat() + 'Z',
            'last_seen': self.last_seen.isoformat() + 'Z',
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                # 'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'name', 'phone', 'location', 'about_me', 'status']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def ping(self):
        self.last_seen = datetime.now()

        print(self.login_counts)
        self.login_counts += 1
        print(self.login_counts)

        db.session.commit()

    def get_jwt(self, expires_in=7200):
        return jwt.encode({'id': self.id}, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_jwt(token):
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'])
        except jwt.exceptions.ExpiredSignatureError as e:
            print(e)
            return None

        return User.query.get(payload.get('id'))

    def add_notification(self, name, data):
        '''给用户实例对象增加通知'''
        # 如果具有相同名称的通知已存在，则先删除该通知
        self.notifications.filter_by(name=name).delete()
        # 为用户添加通知，写入数据库
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(32))
    authority = db.Column(db.String(32))
    create_at = db.Column(db.DateTime(), default=datetime.utcnow)
    last_update = db.Column(
        db.DateTime(), onupdate=datetime.utcnow, default=datetime.utcnow)

    users = db.relationship('User', secondary=users_roles,
                            backref=db.backref('roles'))

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class Notification(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.Float, index=True, default=datetime.utcnow)
    payload_json = db.Column(db.Text)

    def __repr__(self):
        return '<Notification {}>'.format(self.id)

    def get_data(self):
        return json.loads(str(self.payload_json))

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'name': self.user.name,
                'avatar': self.user.avatar(128)
            },
            'timestamp': self.timestamp,
            'payload': self.get_data(),
            '_links': {
                'self': url_for('api.get_notification', id=self.id),
                'user_url': url_for('api.get_user', id=self.user_id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['body', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])


class Equipment(db.Model, PaginatedAPIMixin, Serializer):
    __tablename__ = 'equipments'
    __table_args__ = {'sqlite_autoincrement': True}

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    node_name = db.Column(db.String(50))
    equipment_code = db.Column(db.String(50))
    version = db.Column(db.String(50))
    name = db.Column(db.String(50))
    is_online = db.Column(db.String(1), default=0)  # 0: 离线, 1, 在线
    online_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_update = db.Column(db.DateTime)
    status = db.Column(db.String(1), default=0)  # 0: 空闲, 1, 占用
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)

    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('equipment_type.id'))

    users = db.relationship(
        'User', secondary=users_equipments, backref=db.backref('equipments'))
    jobs = db.relationship('Job', backref='equipment', lazy='dynamic')
    poweronoffs = db.relationship(
        'Poweronoff', backref='equipment', lazy='dynamic')

    @classmethod
    def dinamic_filter(model_class, filter_condition):
        __query = db.session.query(model_class)
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception('Invalid filter: %s' % raw)
            column = getattr(model_class, key, None)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                try:
                    attr = list(filter(lambda e: hasattr(column, e %
                                op), ['%s', '%s_', '__%s__']))[0] % op
                except IndexError:
                    raise Exception('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            __query = __query.filter(filt)
        return __query

    def __repr__(self):
        return "{}-{}-{}".format(self.node_name, self.equipment_code, self.name)

    def get_last_job(self):
        jobs = [j.to_dict() for j in self.jobs]
        return jobs[-1] if jobs else None

    def calculate_online_time(self):
        if self.is_online == '1':
            time_difference = datetime.utcnow() - self.online_at
        else:
            time_difference = timedelta(0)

        days = time_difference.days
        seconds = time_difference.seconds

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        # remaining_seconds = seconds % 60
        return (f"{days} 天, {hours} 小时,{minutes} 分钟")

    def to_dict(self):
        data = {
            'id': self.id,
            'node_name': self.node_name,
            'equipment_code': self.equipment_code,
            'version': self.version,
            'type_name': self.type.name if self.type else None,
            'city': self.city.name if self.city else None,
            'name': self.name,
            'is_online': self.is_online,
            'online_at': self.online_at,
            'online_time': self.calculate_online_time(),
            'status': self.status,
            # 'jobs': [j.to_dict() for j in self.jobs],
            # 'last_job': self.get_last_job(),
            'create_at': self.create_at.isoformat() + 'Z',
            'last_update': self.last_update.isoformat() + 'Z' if self.last_update else None,
        }
        return data

    def to_dict_simple(self):
        data = {
            'id': self.id,
            'node_name': self.node_name,
            'equipment_code': self.equipment_code,
            'version': self.version,
            'type_name': self.type.name if self.type else None,
            'city': self.city.name if self.city else None,
            'name': self.name,
            'status': self.status,
            'create_at': self.create_at.isoformat() + 'Z',
            'last_update': self.last_update.isoformat() + 'Z' if self.last_update else None,
        }
        return data

    def from_dict(self, data):
        for field in ['admission_sequence', 'lottery_sequence', 'population', 'phone', 'check_flag', 'choices_printed']:
            if field in data:
                setattr(self, field, data[field])


class EquipmentType(db.Model):
    __tablename__ = 'equipment_type'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)

    equipments = db.relationship('Equipment', backref='type', lazy='dynamic')


class City(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)

    equipments = db.relationship('Equipment', backref='city', lazy='dynamic')


class Poweronoff(db.Model):
    __tablename__ = 'poweronoffs'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)

    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'))


class Job(db.Model, PaginatedAPIMixin, Serializer):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    is_tested = db.Column(db.Integer, default=0)    # 0: initial, 1: tested
    # 0: initial, 1: running 2, ended
    status = db.Column(db.Integer, default=0)
    stage = db.Column(db.Integer, default=0)        # total 10 stages
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)

    equipment_id = db.Column(db.Integer, db.ForeignKey('equipments.id'))
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @classmethod
    def dinamic_filter(model_class, filter_condition):
        __query = db.session.query(model_class)
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception('Invalid filter: %s' % raw)
            column = getattr(model_class, key, None)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                try:
                    attr = list(filter(lambda e: hasattr(column, e %
                                op), ['%s', '%s_', '__%s__']))[0] % op
                except IndexError:
                    raise Exception('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            __query = __query.filter(filt)
        return __query

    def __repr__(self):
        return "{}-{}-{}".format(self.message, self.start_time, self.end_time)

    def to_dict(self):
        data = {
            'id': self.id,
            'action': self.action.to_dict() if self.action else None,
            'equipment': self.equipment.to_dict_simple() if self.equipment else None,
            'status': self.status,
            'is_tested': self.is_tested,
            'stage': self.stage,
            'start_time': self.start_time.isoformat() + 'Z' if self.start_time else None,
            'end_time': self.start_time.isoformat() + 'Z' if self.end_time else None,

            'create_at': self.create_at.isoformat() + 'Z',
            'last_update': self.last_update.isoformat() + 'Z' if self.last_update else None,
        }
        return data

    def from_dict(self, data):
        for field in ['status', 'stage', 'is_tested', 'equipment_id', 'action_id']:
            if field in data:
                setattr(self, field, data[field])


class ActionType(db.Model):
    __tablename__ = 'action_type'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    action_code = db.Column(db.String(50))           # A1 A2 B1 B2 C1 C2
    is_mortise = db.Column(db.Integer(), default=0)  # 0 tenon, 1 mortise
    assembly_type = db.Column(db.String(1), default='0')  # 0 单排， 1 双排， 2 复合

    actions = db.relationship('Action', backref='action_type', lazy='dynamic')


class Action(db.Model, PaginatedAPIMixin, Serializer):
    __tablename__ = 'actions'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))

    knife_diameter = db.Column(db.Integer())
    knife_b_diameter = db.Column(db.Integer())
    knife_b_angle = db.Column(db.Integer())
    base_width = db.Column(db.Integer())
    base_thickness = db.Column(db.Integer())
    base_length = db.Column(db.Integer())

    # is_tenon_b_needed = db.Column(db.Integer())
    tenon_interval = db.Column(db.Integer())
    alignment = db.Column(db.String(1))     # 0: 居中, 1: 1/2燕尾宽,  2: 自定义
    left_margin = db.Column(db.Integer())
    right_margin = db.Column(db.Integer())

    tenon_a_width = db.Column(db.Integer())
    tenon_a_thickness = db.Column(db.Integer())
    tenon_a_length = db.Column(db.Integer())
    tenon_a_left = db.Column(db.Integer())
    tenon_a_bottom = db.Column(db.Integer())
    number_of_tenona = db.Column(db.Integer())

    tenon_b_width = db.Column(db.Integer())
    tenon_b_thickness = db.Column(db.Integer())
    tenon_b_length = db.Column(db.Integer())
    tenon_b_left = db.Column(db.Integer())
    tenon_b_bottom = db.Column(db.Integer())

    tenon_c_width = db.Column(db.Integer())
    tenon_c_thickness = db.Column(db.Integer())
    tenon_c_length = db.Column(db.Integer())
    tenon_c_left = db.Column(db.Integer())
    tenon_c_bottom = db.Column(db.Integer())

    tenon_d_width = db.Column(db.Integer())
    tenon_d_thickness = db.Column(db.Integer())
    tenon_d_length = db.Column(db.Integer())
    tenon_d_left = db.Column(db.Integer())
    tenon_d_bottom = db.Column(db.Integer())

    corner_radius = db.Column(db.Integer())
    left_distance = db.Column(db.Integer())
    bottom_distance = db.Column(db.Integer())
    cutting_depth_perlayer = db.Column(db.Integer())
    lightness = db.Column(db.Integer())
    create_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('action_type.id'))

    jobs = db.relationship('Job', backref='action', lazy='dynamic')

    @classmethod
    def dinamic_filter(model_class, filter_condition):
        __query = db.session.query(model_class)
        for raw in filter_condition:
            try:
                key, op, value = raw
            except ValueError:
                raise Exception('Invalid filter: %s' % raw)
            column = getattr(model_class, key, None)
            if not column:
                raise Exception('Invalid filter column: %s' % key)
            if op == 'in':
                if isinstance(value, list):
                    filt = column.in_(value)
                else:
                    filt = column.in_(value.split(','))
            else:
                try:
                    attr = list(filter(lambda e: hasattr(column, e %
                                op), ['%s', '%s_', '__%s__']))[0] % op
                except IndexError:
                    raise Exception('Invalid filter operator: %s' % op)
                if value == 'null':
                    value = None
                filt = getattr(column, attr)(value)
            __query = __query.filter(filt)
        return __query

    def __repr__(self):
        return "{}".format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'knife_diameter': self.knife_diameter,
            'knife_b_diameter': self.knife_b_diameter,
            'knife_b_angle': self.knife_b_angle,

            'base_width': self.base_width,
            'base_thickness': self.base_thickness,
            'base_length': self.base_length,

            # 'is_tenon_b_needed': self.is_tenon_b_needed,
            'tenon_interval': self.tenon_interval,
            'alignment': self.alignment,
            'left_margin': self.left_margin,
            'right_margin': self.right_margin,

            'tenon_a_width': self.tenon_a_width,
            'tenon_a_thickness': self.tenon_a_thickness,
            'tenon_a_length': self.tenon_a_length,
            'tenon_a_left': self.tenon_a_left,
            'tenon_a_bottom': self.tenon_a_bottom,
            'number_of_tenona': self.number_of_tenona,

            'tenon_b_width': self.tenon_b_width,
            'tenon_b_thickness': self.tenon_b_thickness,
            'tenon_b_length': self.tenon_b_length,
            'tenon_b_left': self.tenon_b_left,
            'tenon_b_bottom': self.tenon_b_bottom,

            'tenon_c_width': self.tenon_c_width,
            'tenon_c_thickness': self.tenon_c_thickness,
            'tenon_c_length': self.tenon_c_length,
            'tenon_c_left': self.tenon_c_left,
            'tenon_c_bottom': self.tenon_c_bottom,

            'tenon_d_width': self.tenon_d_width,
            'tenon_d_thickness': self.tenon_d_thickness,
            'tenon_d_length': self.tenon_d_length,
            'tenon_d_left': self.tenon_d_left,
            'tenon_d_bottom': self.tenon_d_bottom,

            'corner_radius': self.corner_radius,
            # 'left_distance': self.left_distance,
            # 'bottom_distance': self.bottom_distance,
            'cutting_depth_perlayer': self.cutting_depth_perlayer,
            'lightness': self.lightness,

            'create_at': self.create_at.isoformat() + 'Z',
            'last_update': self.last_update.isoformat() + 'Z' if self.last_update else None,
            'user_id': self.user_id,

            'type_id': self.type_id,
            'action_type': self.action_type.name if self.type_id else None,
            'action_code': self.action_type.action_code if self.type_id else None,
            'assembly_type': self.action_type.assembly_type if self.type_id else '0',
            'is_mortise': self.action_type.is_mortise if self.type_id else 0,

            'gcodefile': self.last_update.strftime("%Y%m%d_%H%M%S") + '.nc' if self.last_update else self.create_at.strftime("%Y%m%d_%H%M%S") + '.nc'
        }
        return data

    def from_dict(self, data):
        for field in [
            'name',
            'knife_diameter',
            'knife_b_diameter',
            'knife_b_angle',

            'base_width',
            'base_thickness',
            'base_length',

            # 'is_tenon_b_needed',
            'tenon_interval',
            'left_margin',
            'right_margin',
            'alignment',

            'tenon_a_width',
            'tenon_a_thickness',
            'tenon_a_length',
            'tenon_a_left',
            'tenon_a_bottom',
            'number_of_tenona',

            'tenon_b_width',
            'tenon_b_thickness',
            'tenon_b_length',
            'tenon_b_left',
            'tenon_b_bottom',

            'tenon_c_width',
            'tenon_c_thickness',
            'tenon_c_length',
            'tenon_c_left',
            'tenon_c_bottom',

            'tenon_d_width',
            'tenon_d_thickness',
            'tenon_d_length',
            'tenon_d_left',
            'tenon_d_bottom',

            'corner_radius',
            'cutting_depth_perlayer',
            'lightness',
            'equipment_id'
        ]:
            if field in data:
                setattr(self, field, data[field])
