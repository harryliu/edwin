# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import
from __future__ import with_statement
from . import database_meta
from . import database_tera


def closeAllConnections():
    database_meta.closeConnection()
    database_tera.closeConnection()
