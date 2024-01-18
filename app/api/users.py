import re
from flask import request, jsonify, url_for, g
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from app.models import User
# from flask_babel import gettext as _

@bp.route('/users', methods=['POST'])
def create_user():
    '''注册一个新用户'''
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))

    message = {}
    if 'username' not in data or not data.get('username', None):
        message['username'] = _('Please provide a valid username.')
    pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    if 'email' not in data or not re.match(pattern, data.get('email', None)):
        message['email'] = _('Please provide a valid email address.')
    if 'password' not in data or not data.get('password', None):
        message['password'] = _('Please provide a valid password.')

    if User.query.filter_by(username=data.get('username', None)).first():
        message['username'] = 'Please use a different username.'
    if User.query.filter_by(email=data.get('email', None)).first():
        message['email'] = _('Please use a different email address.')
    if message:
        return bad_request(message)

    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response


@bp.route('/users', methods=['GET'])
# @token_auth.login_required
def get_users():
    '''返回用户集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    get_name = 'name' in request.args and request.args.get('name') != ''  

    conditions = []
    userIdList = []

    if get_name:
        name = request.args.get('name')
        search_name = "%{}%".format(name)

        userFromUsername = User.query.filter(User.username.like(search_name))
        userFromName = User.query.filter(User.name.like(search_name))
        userFromNickname = User.query.filter(User.nickname.like(search_name))

        for u in userFromUsername:
            userIdList.append(u.id)

        for u in userFromName:
            userIdList.append(u.id)

        for u in userFromNickname:
            userIdList.append(u.id)

        conditions.append(('id', 'in', userIdList))

    query = User.dinamic_filter(conditions).order_by(User.login_counts.desc())
    data = User.to_collection_dict(query, page, per_page)
    return jsonify(data)



@bp.route('/users/<int:id>', methods=['GET'])
# @token_auth.login_required
def get_user(id):
    '''返回一个用户'''
    user = User.query.get_or_404(id)

    print(jsonify(User.query.get_or_404(id).to_dict()))
    if g.current_user == user:
        return jsonify(User.query.get_or_404(id).to_dict(include_email=True))
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users/<int:id>', methods=['DELETE'])
# @token_auth.login_required
def delete_user(id):
    '''返回一条图书记录'''
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    response = jsonify({'info': 'users deleted by id:' + str(id) })
    response.status_code = 200
    return response




@bp.route('/role/', methods=['GET'])
@token_auth.login_required
def get_role():
    return jsonify(g.current_user.to_dict())




@bp.route('/users/project/<int:id>', methods=['GET'])
@token_auth.login_required
def get_myproject(id):
    '''返回一个用户'''
    user = User.query.get_or_404(id)
    
    project_list = []
    for record in user.records:
        project_list.append(record.template.project)

    print(str(project_list))
    data = []
    for project in project_list:
        p = {
        "id": project.id,
        "name": project.name,
        "isDone": project.get_receiver_log()
        }
        if p not in data:
            data.append(p)

    
    return jsonify(data)


@bp.route('/users/<int:id>', methods=['PUT', 'POST'])
@token_auth.login_required
def update_user(id):
    '''修改一个用户'''
    user = User.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return bad_request(_('You must post JSON data.'))

    message = {}
    if 'username' in data and not data.get('username', None):
        message['username'] = 'Please provide a valid username.'

    pattern = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$'
    if 'email' in data and not re.match(pattern, data.get('email', None)):
        message['email'] = 'Please provide a valid email address.'

    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        message['username'] = 'Please use a different username.'

    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        message['email'] = 'Please use a different email address.'

    if message:
        return bad_request(message)

    user.from_dict(data, new_user=False)
    user.status = 1
    db.session.commit()
    return jsonify(user.to_dict())



@bp.route('/users/<int:id>/notifications/', methods=['GET'])
@token_auth.login_required
def get_user_notifications(id):
    '''返回该用户的新通知'''
    user = User.query.get_or_404(id)
    if g.current_user != user:
        return error_response(403)
    # 只返回上次看到的通知以来发生的新通知
    # 比如用户在 10:00:00 请求一次该API，在 10:00:10 再次请求该API只会返回 10:00:00 之后产生的新通知
    since = request.args.get('since', 0.0, type=float)
    notifications = user.notifications.filter(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([n.to_dict() for n in notifications])





@bp.route('/user/info', methods=['GET'])
@token_auth.login_required
def get_userinfo():
    if g.current_user:
        return jsonify(g.current_user.to_dict())
    else:
        return error_response(50014)


@bp.route('/user/logout', methods=['POST'])
@token_auth.login_required
def logout():
    return 'log out'


