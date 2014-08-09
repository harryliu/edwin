# -*- coding: utf-8 -*-
'''

'''


from __future__ import absolute_import
import json
import urllib2
from . import conf
import logging


def _updateResult(check_itm, check_value, status, detail_msg, notification_msg=''):
    logger = logging.getLogger(__name__)
    logger.info("Begin to update checking result via web API.")

    data = {'status': status,
            'value': check_value,
            'detail_msg': detail_msg,
            'notification_msg': notification_msg
            }
    data_json = json.dumps(data)
    url = "%s/api/v1.0/checks/%s" % (conf.web_url, check_itm)
    req = urllib2.Request(url, data_json, {'Content-Type': 'application/json'})

    f = urllib2.urlopen(req)
    httpCodes = f.getcode()
    responseStr = f.read()
    f.close()
    json_data = json.loads(responseStr)
    echo_msg = json_data['echo_msg']
    successful = httpCodes in [200, 201, 202]
    return (successful, echo_msg)


def updateNonnumericalResult(check_itm, status, detail_msg, notification_msg=''):
    check_value = 0
    return _updateResult(check_itm, check_value, status, detail_msg, notification_msg)


def updateNumericalResult(check_itm, check_value, detail_msg, notification_msg=''):
    status = ""
    return _updateResult(check_itm, check_value, status, detail_msg, notification_msg)


def registerException(check_itm, exception_msg):
    logger = logging.getLogger(__name__)
    logger.info("Begin to register checking exception via web API.")

    data = {
        'exception_msg': exception_msg
        }
    data_json = json.dumps(data)
    url = "%s/api/v1.0/exceptions/%s" % (conf.web_url, check_itm)
    req = urllib2.Request(url, data_json, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    httpCodes = f.getcode()
    responseStr = f.read()
    f.close()
    json_data = json.loads(responseStr)
    echo_msg = json_data['echo_msg']
    successful = httpCodes in [200, 201, 202]
    return (successful, echo_msg)
