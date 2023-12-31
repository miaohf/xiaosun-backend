import re
from flask import request, jsonify, url_for, g
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from app.models import Actions
import uuid
# from flask_babel import gettext as _

@bp.route('/actions', methods=['POST'])
@token_auth.login_required
def create_action():
    '''创建一个作业指令'''
    data = request.get_json()
    print(data)

    data['name'] = data['name'] + '-' + str(uuid.uuid4())[:8]
    action = Actions()  
    action.from_dict(data)
    action.user_id = g.current_user.id
    db.session.add(action)
    db.session.commit()
    
    return jsonify({'result': 'ok'})


@bp.route('/actions', methods=['GET'])
@token_auth.login_required
def get_actions():
    '''返回作业指令集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 100, type=int), 100)
    conditions = []
    conditions.append(('user_id', 'eq', g.current_user.id))
    query = Actions.dinamic_filter(conditions).order_by(Actions.create_at.desc())
    data = Actions.to_collection_dict(query, page, per_page)
    return jsonify(data)



@bp.route('/actions/<int:id>', methods=['PUT'])
# @token_auth.login_required
def get_action(id):
    '''更新一个作业指令'''
    data = request.get_json()
    print(type(data), data)
    action = Actions.query.get_or_404(id)
    action.from_dict(data)
    db.session.commit()

    return jsonify(action.to_dict())


@bp.route('/actions/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_action(id):
    '''删除作业指令'''
    action = Actions.query.get_or_404(id)
    db.session.delete(action)
    db.session.commit()
    response = jsonify({'info': 'action deleted by id:' + str(id) })
    response.status_code = 200
    return response










# @bp.route('/equipments/<int:id>', methods=['PUT', 'POST'])
# @token_auth.login_required
# def updateequipment(id):
#     '''修改一个设备'''
#     user = Users.query.get_or_404(id)
#     data = request.get_json()
#     if not data:
#         return bad_request(_('You must post JSON data.'))

#     message = {}
#     if 'username' in data and not data.get('username', None):
#         message['username'] = 'Please provide a valid username.'

#     pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
#     if 'email' in data and not re.match(pattern, data.get('email', None)):
#         message['email'] = 'Please provide a valid email address.'

#     if 'username' in data and data['username'] != user.username and \
#             Users.query.filter_by(username=data['username']).first():
#         message['username'] = 'Please use a different username.'

#     if 'email' in data and data['email'] != user.email and \
#             Users.query.filter_by(email=data['email']).first():
#         message['email'] = 'Please use a different email address.'

#     if message:
#         return bad_request(message)

#     user.from_dict(data, newequipment=False)
#     user.status = 1
#     db.session.commit()
#     return jsonify(user.to_dict())

