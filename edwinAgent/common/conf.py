# -*- coding: utf-8 -*-
'''
'''
from __future__ import absolute_import
import logging

# edwinServer.web site url
web_url = "http://10.100.10.1:5000"


# logging
log_level = logging.INFO


# Maybe you want to check data in your some database.
# Configure db connection here, then you can access it in your agent
tera_driver_jdbc = "com.teradata.jdbc.TeraDriver"
tera_url_jdbc = "jdbc:teradata://10.100.100.101/DATABASE=dbc,TMODE=ANSI,CHARSET=UTF8,LOB_SUPPORT=off"
tera_uid_jdbc = "your_account"
tera_pwd_jdbc = "your_pwd"
