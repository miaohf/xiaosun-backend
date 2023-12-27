import re
from flask import request, jsonify, url_for, g
from app import db
from app.api import bp
from app.api.auth import token_auth
from app.api.errors import bad_request
from flask_babel import gettext as _
import os, uuid
import os.path as op
from werkzeug import secure_filename
import app

from app.models import Books, Audios




UPLOAD_BASE = '/var/www/booksapi/'
URL_BASE = 'http://booksapi.coloredeer.com:8004/'

uploadTypes = {
    'image': {
        'ext': ['png', 'jpg', 'jpeg'],
        'dir': 'images'
        },
    'audio': {
        'ext': ['mp3','aac'],
        'dir': 'audios'
        }
    }


@bp.route('/upload', methods=['POST'])
# @token_auth.login_required
def upload():

    id = request.args.get('id', type=int)
    type = request.args.get('filetype')

    # if not os.path.isdir(UPLOAD_FOLDER):
    #     os.mkdir(UPLOAD_FOLDER)

    file = request.files['file']
    filename = file.filename
    
    # Gen GUUID File Name
    fileExt = filename.split('.')[-1]
    # filePrefix = filename.split('.')[0]
    
    for i in uploadTypes:
        if fileExt in uploadTypes[i]['ext']:
            autoGenFileName = uuid.uuid4()
            newFileName = str(autoGenFileName) + '.' + fileExt
            file.save(os.path.join(UPLOAD_BASE + uploadTypes[i]['dir'], newFileName))

            # Save file Info into DB
            book = Books.query.get_or_404(id)
            url_string = URL_BASE + uploadTypes[i]['dir'] + '/' + newFileName
            if i == 'image':         
                book.pic = url_string
            else:
                audio = Audios()
                # audio.title = str(autoGenFileName)
                audio.title = book.title + '_' + str(len(book.audios) + 1).zfill(2)               
                audio.url = url_string
                db.session.add(audio)
                book.audios.append(audio)

    db.session.commit()

    # data = {
    # 	id: file.id,
    # 	filename: file.filename
    # }

    return ('OK')



@bp.route('/remove', methods=['DELETE'])
# @token_auth.login_required
def delete_file():

    filetype = request.args.get('type')
    uploadid = request.args.get('id', type=int)
    print(filetype, uploadid)

    # Save file Info into DB
    if filetype == 'contract':
        file = Contractfile.query.get(uploadid)
    elif filetype == 'maintenance':
        file = Maintenancefile.query.get(uploadid)
        print(file.name)
    elif filetype == 'petition':
        file = Petitionfile.query.get(uploadid)
        print(file.name)

    db.session.delete(file)
    db.session.commit()
    return ('OK')
