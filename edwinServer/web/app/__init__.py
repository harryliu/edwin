# -*- coding: utf-8 -*-
'''
Created on 2014-2-10

'''
from __future__ import absolute_import, print_function, unicode_literals
from flask import Flask, g, render_template, send_from_directory, make_response, jsonify
import os
import os.path
from .excepts import InvalidUsage
from ...common import database_meta
from .api import mod as checksModule
from .views import mod as dashboardModule

_basedir = os.path.abspath(os.path.dirname(__file__))
configPy = os.path.join(os.path.join(_basedir, os.path.pardir), 'conf.py')

app = Flask(__name__)  # create our application object
app.config.from_pyfile(configPy)

flask_sqlalchemy_used = False  # when Flask-SQLAlchemy used


# if app.debug:
#     from flask_debugtoolbar import DebugToolbarExtension
#     toolbar = DebugToolbarExtension(app)

app.register_blueprint(checksModule)
app.register_blueprint(dashboardModule)


def connect_db():   # when Flask-SQLAlchemy not used
    return database_meta.openConnection()


def close_db():
    database_meta.closeConnection()


@app.before_request
def before_request():
    app.logger.info("before_request() called.")

    """Make sure we are connected to the database each request."""
    if not flask_sqlalchemy_used:
        connect_db()


@app.teardown_request
def teardown_request(response):
    app.logger.info("after_request() called.")

    """Closes the database again at the end of the request."""
    if not flask_sqlalchemy_used:
        close_db()
    return response


#----------------------------------------
# controllers
#----------------------------------------
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/")
def index():
    return render_template('index.html')


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(404)
def page_not_found(error):
    app.logger.exception(error)
    return make_response(jsonify({'error': 'Not found'}), 404)
