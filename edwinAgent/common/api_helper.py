# -*- coding: utf-8 -*-
'''

'''


from __future__ import absolute_import
import json
import urllib2
from . import conf
import logging


class check_item_cfg(object):

    def __init__(self):
        self.itm_code = ""
        self.itm_title = ""
        self.itm_category = ""
        self.enabled_flag = ""
        self.host = ""
        self.check_script = ""
        self.check_interval_minute = ""
        self.check_value_is_number = ""
        self.description = ""
        self.warning_limit = ""
        self.critical_limit = ""
        self.shadow_data = ""
        self.owner_team_list = ""
        self.warning_mail_cc = ""
        self.critical_mail_cc = ""
        self.critical_sms_flag = ""
        self.critical_call_flag = ""
        self.allow_repeated_sms_alarm = ""
        self.allow_repeated_call_alarm = ""
        self.allow_repeated_mail_alarm = ""


def _updateResult(check_itm, check_value, status, detail_msg, notification_msg=''):
    logger = logging.getLogger(__name__)
    logger.info("Begin to update checking result via web API.")

    data = {'status': status,
            'value': check_value,
            'detail_msg': detail_msg,
            'notification_msg': notification_msg
            }
    data_json = json.dumps(data)
    url = "%s/api/v1.0/results/%s" % (conf.web_url, check_itm)
    req = urllib2.Request(url, data_json, {'Content-Type': 'application/json'})

    f = urllib2.urlopen(req)
    httpCodes = f.getcode()
    responseStr = f.read()
    f.close()
    json_data = json.loads(responseStr)
    echo_msg = json_data['echo_msg']
    successful = httpCodes in [200, 201, 202]
    return (successful, echo_msg)


def getCheckItemCfg(check_itm):
    logger = logging.getLogger(__name__)
    logger.info("Begin to get check item %s configuration info." % (check_itm))

    url = "%s/api/v1.0/info/%s" % (conf.web_url, check_itm)
    req = urllib2.Request(url)

    f = urllib2.urlopen(req)
    httpCodes = f.getcode()
    responseStr = f.read()
    f.close()
    json_data = json.loads(responseStr)
    result = check_item_cfg()
    successful = httpCodes in [200, 201, 202]
    if successful:
        result.itm_code = json_data['itm_code']
        result.itm_title = json_data['itm_title']
        result.itm_category = json_data['itm_category']
        result.enabled_flag = json_data['enabled_flag']
        result.host = json_data['host']
        result.check_script = json_data['check_script']
        result.check_interval_minute = json_data['check_interval_minute']
        result.check_value_is_number = json_data['check_value_is_number']
        result.description = json_data['description']
        result.warning_limit = json_data['warning_limit']
        result.critical_limit = json_data['critical_limit']
        result.shadow_data = json_data['shadow_data']
        result.owner_team_list = json_data['owner_team_list']
        result.warning_mail_cc = json_data['warning_mail_cc']
        result.critical_mail_cc = json_data['critical_mail_cc']
        result.critical_sms_flag = json_data['critical_sms_flag']
        result.critical_call_flag = json_data['critical_call_flag']
        result.allow_repeated_sms_alarm = json_data['allow_repeated_sms_alarm']
        result.allow_repeated_call_alarm = json_data['allow_repeated_call_alarm']
        result.allow_repeated_mail_alarm = json_data['allow_repeated_mail_alarm']
    return result


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
