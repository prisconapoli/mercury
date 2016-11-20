#!/usr/bin/env python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from config import config,Config
from flask_moment import Moment
from flask_cache import Cache
from celery import Celery

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
cache = Cache()
queue = Celery(__name__, broker=Config.CELERY_BROKER_URL)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    cache.init_app(app)
    queue.conf.update(app.config)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api_1_0 import api as api_1_0_blueprint, version
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/'+version)
    return app
