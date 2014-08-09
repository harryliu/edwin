# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import
import logging

# logging
log_level = logging.INFO
log_level = logging.DEBUG


# edwinServer odbc configuration
metadb_url_odbc = "DSN=my_edwin_database;UID=username_abc;PWD=pwd_123"


# script run mode for alarm_send.py
alarm_send_in_daemon_mode = False


# email account for alarm_send.py
use_mailx_settings = False
smtp_host = "smtp.gmail.com"
smtp_port = 465
smtp_over_ssl = True
mail_user = "SENDER@gmail.com"
mail_pwd = "MYPASSWD"


# edwin web url
# This url will be embedded in notification email.
# Be noted that host should not be localhost, 127.0.0.1 , 0.0.0.0
web_url = "http://10.100.10.1:5000"
