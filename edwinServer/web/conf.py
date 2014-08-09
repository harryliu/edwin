# -*- coding: utf-8 -*-
'''
Created on 2014-2-10

'''
from __future__ import absolute_import
import os
from datetime import timedelta
_basedir = os.path.abspath(os.path.dirname(__file__))


depoly_on_cherrypy = True

PORT = 5000
DEBUG = True  # enable reload

SECRET_KEY = os.urandom(24)
PERMANENT_SESSION_LIFETIME = timedelta(seconds=24 * 60 * 60)

CSRF_ENABLED = True
CSRF_SESSION_KEY = SECRET_KEY
