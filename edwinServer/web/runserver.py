# -*- coding: utf-8 -*-
'''
Created on 2014-2-10

'''

from __future__ import absolute_import
from edwinServer.web.app import app
import logging
import logging.config
from edwinServer.web import conf as web_conf
from edwinServer.common import conf
from edwinServer.common import my_logging
from edwinServer.common import os_helper


# logging.basicConfig(level=logging.DEBUG)      # use for development
log_file = os_helper.getLoggingFileName(__file__)
root_logger = logging.getLogger()
my_logging.configureLogger(root_logger, log_file, conf.log_level)


def run_on_default_server():
    if app.debug:
        # app.run(port=PORT, debug=True)                  # disable to access on other computer
        app.run(host='0.0.0.0', port=web_conf.PORT, debug=True)  # allow to access on other computer
    else:
        app.run(host='0.0.0.0', port=web_conf.PORT,)


def run_on_cherrypy_server():
    if app.debug:
        run_on_cherrypy_auto_reload()
    else:
        run_on_cherrypy_for_production()


def run_on_cherrypy_auto_reload():
    '''
    run on cherrypy with auto_reload option 
    '''
    import cherrypy

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': web_conf.PORT,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()


def run_on_cherrypy_for_production():
    '''
    run on cherrypy without auto_reload option
    '''
    from cherrypy import wsgiserver
    dispatch = wsgiserver.WSGIPathInfoDispatcher({'/': app})
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', web_conf.PORT), dispatch)

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    if web_conf.depoly_on_cherrypy:
        run_on_cherrypy_server()
    else:
        run_on_default_server()
