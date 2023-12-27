import re
from flask import request, jsonify, url_for, g
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request, error_response
from app.models import Jobs, Equipments
# from flask_babel import gettext as _


@bp.route('/jobs', methods=['POST'])
@token_auth.login_required
def create_job():
    '''创建一个任务'''
    data = request.get_json()
    print('data: ', data)
    job = Jobs()
    job.from_dict(data)
    job.user_id = g.current_user.id
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict())


@bp.route('/jobs', methods=['GET'])
@token_auth.login_required
def get_jobs():
    '''返回作業集合，分页'''
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    conditions = []
    conditions.append(('user_id', 'eq', g.current_user.id))

    query = Jobs.dinamic_filter(conditions).order_by(Jobs.create_at.desc())
    data = Jobs.to_collection_dict(query, page, per_page)
    return jsonify(data)


@bp.route('/jobs/options', methods=['GET'])
@token_auth.login_required
def get_options():
    '''返回下拉菜單選項，分页'''
    data = {
        'actions': [{'id': a.id, 'name': a.name} for a in g.current_user.actions],
        'equipments': [{'id': em.id, 'name': em.name} for em in g.current_user.equipments],
    }

    return jsonify(data)

# @bp.route('/equipments/<int:id>', methods=['GET'])
# # @token_auth.login_required
# def get_equipment(id):
#     '''返回一个设备'''
#     equipment = Equipments.query.get_or_404(id)

#     return jsonify(equipment.to_dict())


@bp.route('/jobs/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_job(id):
    '''删除指令'''
    job = Jobs.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    response = jsonify({'info': 'jobs deleted by id:' + str(id) })
    response.status_code = 200
    return response


@bp.route('/jobs/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_job(id):
    '''更新一个指令'''
    job = Jobs.query.get_or_404(id)
    data = request.get_json()
    print('data: ', data)
    job.from_dict(data)
    
    # equipment = Equipments.query.get(data['equipment_id'])
    # equipment.status == 0
    db.session.commit()
    return jsonify(job.to_dict())
