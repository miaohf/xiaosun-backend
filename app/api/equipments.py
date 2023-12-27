import re
from flask import request, jsonify, url_for, g
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from app.models import Equipments
# from flask_babel import gettext as _

# @bp.route('/equipments', methods=['POST'])
# def createequipment():
#     '''注册一个新设备'''
#     data = request.get_json()

#     return response


@bp.route('/equipments', methods=['GET'])
@token_auth.login_required
def get_equipments():
    '''返回设备集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 100, type=int), 100)
    equipment_id_list = [em.id for em in g.current_user.equipments] 
    conditions = []
    conditions.append(('id', 'in', equipment_id_list))
    query = Equipments.dinamic_filter(conditions).order_by(Equipments.last_update.desc())
    data = Equipments.to_collection_dict(query, page, per_page)
    return jsonify(data)



@bp.route('/equipments/<int:id>', methods=['GET'])
# @token_auth.login_required
def get_equipment(id):
    '''返回一个设备'''
    equipment = Equipments.query.get_or_404(id)

    return jsonify(equipment.to_dict())


# @bp.route('/equipments/<int:id>', methods=['DELETE'])
# @token_auth.login_required
# def deleteequipment(id):
#     '''删除设备'''
#     user = Users.query.get_or_404(id)
#     db.session.delete(user)
#     db.session.commit()
#     response = jsonify({'info': 'users deleted by id:' + str(id) })
#     response.status_code = 200
#     return response










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

