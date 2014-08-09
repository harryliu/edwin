# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import
from __future__ import with_statement
import logging
import threading
from . import os_helper
if os_helper.isJython():
    from com.ziclix.python.sql import zxJDBC
else:
    from ..site_packages import pypyodbc
from . import conf


# connection=None  # use global connection object to keep connection
threadVar = threading.local()  # thread local variable to keep connection


def closeConnection_jdbc():
    logger = logging.getLogger(__name__)
    #global connection
    try:
        _ = threadVar.connection
    except:
        threadVar.connection = None

    if (threadVar.connection is not None) and (threadVar.connection.closed == False):
        threadVar.connection.close()
        logger.info("Disconnect meta database.")
        threadVar.connection = None


def closeConnection_odbc():
    logger = logging.getLogger(__name__)
    #global connection
    try:
        _ = threadVar.connection
    except:
        threadVar.connection = None

    if (threadVar.connection is not None) and (threadVar.connection.connected):
        threadVar.connection.close()
        logger.info("Disconnect meta database.")
        threadVar.connection = None


def openConnection_jdbc():
    logger = logging.getLogger(__name__)
    #global connection
    try:
        _ = threadVar.connection
    except:
        threadVar.connection = None

    if threadVar.connection is None:
        logger.info('To get database meta connection')
        threadVar.connection = zxJDBC.connect(conf.metadb_url_jdbc, conf.metadb_uid_jdbc, conf.metadb_pwd_jdbc, conf.metadb_driver_jdbc)
        logger.info('Meta connection: %s', (threadVar.connection,))
    logger.debug("DB connection used: %s", threadVar.connection)
    return threadVar.connection


def openConnection_odbc():
    logger = logging.getLogger(__name__)
    #global connection
    try:
        _ = threadVar.connection
    except:
        threadVar.connection = None

    if threadVar.connection is None:
        logger.info('To get database meta connection')
        threadVar.connection = pypyodbc.connect(conf.metadb_url_odbc)
        logger.info('Meta connection: %s', (threadVar.connection,))
    return threadVar.connection


if os_helper.isJython():
    openConnection = openConnection_jdbc
    closeConnection = closeConnection_jdbc
else:
    openConnection = openConnection_odbc
    closeConnection = closeConnection_odbc
