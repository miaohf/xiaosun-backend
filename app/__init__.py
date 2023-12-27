from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from .extensions import scheduler

# from flask_marshmallow import Marshmallow

# from flask_babel import Babel


# # Flask-Babel plugin
# babel = Babel()


# Flask-SQLAlchemy plugin
db = SQLAlchemy()
# # Flask-Migrate plugin
migrate = Migrate()

# ma = Marshmallow()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    scheduler.init_app(app)

    from . import tasks  # noqa: F401

    scheduler.start()

    # Enable CORS
    # CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app, resources={r"/mp/*": {"origins": "*"}})
    CORS(app, resources={r"/sms/*": {"origins": "*"}})
    # Init Flask-SQLAlchemy
    db.init_app(app)
    # Init Flask-Migrate
    migrate.init_app(app, db)

    # babel.init_app(app)

    # ma.init_app(app)

    # 注册 blueprint
    from app.api import bp as api_bp
    # from app.mp import bp as mp_bp
    # from app.sms import bp as sms_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    # app.register_blueprint(mp_bp, url_prefix='/mp')
    # app.register_blueprint(sms_bp, url_prefix='/sms')

    return app

# @babel.localeselector
# def get_locale():
#     # return 'zh'  # 这样设置的话，所有用户永远显示中文
#     return request.accept_languages.best_match(app.config['LANGUAGES'])

from app import models


