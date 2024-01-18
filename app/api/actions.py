import re
import json
from flask import request, jsonify, g
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from app.models import Action, ActionType
import uuid
# from flask_babel import gettext as _


def get_action_type(action_code):
    return ActionType.query.filter(ActionType.action_code == action_code).first()


@bp.route('/actions', methods=['POST'])
@token_auth.login_required
def create_action():
    '''创建或克隆一个作业指令'''
    data = request.get_json()
    print("data['action_code']: ", data['action_code'])

    print('data: ', json.dumps(data, indent=4))

    length_columns = ['tenon_a_length', 'tenon_b_length',
                      'tenon_c_length', 'tenon_d_length']

    if data['is_clone_from_tenon']:
        action_type = get_action_type(int(data['action_code']) + 1)
        data['name'] = action_type.name + '-' + \
            data['name'].split('-')[1] if action_type else None
        data['cutting_depth_perlayer'] = data['cutting_depth_perlayer'] / 2
        for lc in length_columns:
            if lc in data:
                data[lc] = data[lc] + 1 if data[lc] else None
    else:
        action_type = get_action_type(data['action_code'])

    action = Action()
    action.from_dict(data)
    action.type_id = action_type.id if action_type else None
    action.user_id = g.current_user.id
    db.session.add(action)
    db.session.commit()

    print('--- response data in create_action: ',
          json.dumps(action.to_dict(), indent=4))

    return jsonify({'data': action.to_dict()})


@bp.route('/actions', methods=['GET'])
@token_auth.login_required
def get_actions():
    '''返回作业指令集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 100, type=int), 100)
    conditions = []
    conditions.append(('user_id', 'eq', g.current_user.id))
    query = Action.dinamic_filter(conditions).order_by(Action.create_at.desc())
    data = Action.to_collection_dict(query, page, per_page)
    return jsonify(data)


@bp.route('/actions/<int:id>', methods=['PUT'])
# @token_auth.login_required
def get_action(id):
    '''更新一个作业指令'''
    data = request.get_json()
    print('- request data in update_action: ', json.dumps(data, indent=4))

    action = Action.query.get_or_404(id)
    action.from_dict(data)
    db.session.commit()
    print('- response data in update_action: : ', json.dumps(action.to_dict(), indent=4))

    return jsonify({'data': action.to_dict()})


@bp.route('/actions/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_action(id):
    '''删除作业指令'''
    action = Action.query.get_or_404(id)
    db.session.delete(action)
    db.session.commit()
    response = jsonify({'info': 'action deleted by id:' + str(id)})
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
