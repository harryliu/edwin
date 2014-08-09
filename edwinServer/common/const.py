# -*- coding: utf-8 -*-
'''
constant 
'''

from __future__ import absolute_import

# root node of web side bar
DASHBOARD_NODE = '[Dash board]'


# web page/pagelet summary status, please DO NOT change
SUMMARY_STATUS_NORMAL = "Normal"
SUMMARY_STATUS_OUTDATED = "Outdated"
SUMMARY_STATUS_WARNING = "Warning"
SUMMARY_STATUS_CRITICAL = "Critical"


# check status, please DO NOT change
CHECK_STATUS_NORMAL = "NORMAL"
CHECK_STATUS_WARN = "WARNING"
CHECK_STATUS_CRITICAL = "CRITICAL"


# check value for non-numerical check item,  please DO NOT change
CHECK_VALUE_NA = 'NA'


# alarm send status, please DO NOT change
ALARM_SEND_STATUS_WAITING = 'WAITING'
ALARM_SEND_STATUS_SENDING = 'SENDING'
ALARM_SEND_STATUS_FAILED = 'FAILED'
ALARM_SEND_STATUS_SUCCESSFUL = 'SUCCESSFUL'
ALARM_SEND_STATUS_NA = 'NA'


# built-in and sample check item list, please DO NOT change.
# The following check items need to add in table of edwin_check_cfg
# if other check item failed to run, the system will notify out
CHECK_ITEM_BUILTIN_EXCEPTION_NOTIFY = 'BUILTIN_EXCEPTION_NOTIFY'


# alarm mail subject prefix, change it by yourself
EMAIL_SUBJECT_PREFIX_WARN = 'Edwin warning alert'
EMAIL_SUBJECT_PREFIX_CRITICAL = 'Edwin critical alert'
