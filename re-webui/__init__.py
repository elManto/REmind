import os
import json
from flask import Flask, session
from flask_cors import CORS



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='41a78c92f75a4e57b78ec0f1df68f5fb'
    )
    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
#    try:
#        os.makedirs(app.instance_path)
#    except OSError:
#        pass

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import rev_webui
    app.register_blueprint(rev_webui.bp)
    app.add_url_rule('/', endpoint='index')

    from . import first_chall
    app.register_blueprint(first_chall.bp)
#
#    #from . import second_chall
#    #app.register_blueprint(second_chall.bp)
#
#    #from . import third_chall
#    #app.register_blueprint(third_chall.bp)
#
    from . import fourth_chall
    app.register_blueprint(fourth_chall.bp)
#
    from . import fifth_chall
    app.register_blueprint(fifth_chall.bp)
#
#    #from . import sixth_chall
#    #app.register_blueprint(sixth_chall.bp)
#
    from . import seventh_chall
    app.register_blueprint(seventh_chall.bp)
#
#   from . import admin
#   app.register_blueprint(admin.bp)
#
    return app
