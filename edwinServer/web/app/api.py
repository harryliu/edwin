# -*- coding: utf-8 -*-
'''
Created on 2014-2-10

'''
from __future__ import absolute_import
from flask import Blueprint, abort, request, flash, jsonify
from flask.globals import current_app
from ...common.job_state_updater import JobStateUpdater
from ...common.model_meta import dashboard_check_cfg


mod = Blueprint('checks', __name__)  # register the users blueprint module


'''
    checkResult_json = {
        'status': 'NORMAL', 
        'value': 100
        'detail_msg':'Some detailed message' 
        'notification_msg': 'some detailed message for email notification'
    }
    
    exceptionInfo_json = {
        'exception_msg': 'Some exception message'
    }    

'''


@mod.route("/api/v1.0/info/<check_itm_code>", methods=('GET', 'POST'))
def getCheckItemCfg_view(check_itm_code):
    cfg = dashboard_check_cfg.getCfgInDb(check_itm_code)
    if cfg is None:
        flash('Undefined check item %s.' % check_itm_code, 'error')
        current_app.logger.error('getCheckItemCfg_view() function: Undefined check item %s.' % check_itm_code)
        abort(404)  # page not found
    else:
        dic = {'itm_code': cfg.itm_code, 'itm_title': cfg.itm_title, 'itm_category': cfg.itm_category, 'enabled_flag': cfg.enabled_flag, 'host': cfg.host, 'check_script': cfg.check_script, 'check_interval_minute': cfg.check_interval_minute, 'check_value_is_number': cfg.check_value_is_number, 'description': cfg.description, 'warning_limit': cfg.warning_limit, 'critical_limit': cfg.critical_limit, 'shadow_data': cfg.shadow_data, 'owner_team_list': cfg.owner_team_list, 'warning_mail_cc': cfg.warning_mail_cc, 'critical_mail_cc': cfg.critical_mail_cc, 'critical_sms_flag': cfg.critical_sms_flag, 'critical_call_flag': cfg.critical_call_flag, 'allow_repeated_sms_alarm': cfg.allow_repeated_sms_alarm, 'allow_repeated_call_alarm': cfg.allow_repeated_call_alarm, 'allow_repeated_mail_alarm': cfg.allow_repeated_mail_alarm
               }
        return jsonify(dic), 201


@mod.route("/api/v1.0/results/<check_itm_code>", methods=('POST', 'GET'))
@mod.route("/api/v1.0/checks/<check_itm_code>", methods=('POST', 'GET'))
def saveCheckResultAPI_view(check_itm_code):
    state_updater = JobStateUpdater(check_itm_code)
    if state_updater.isUndefinedCheckItem():
        flash('Undefined check item %s.' % check_itm_code, 'error')
        current_app.logger.error('saveCheckResultAPI_view() function: Undefined check item %s.' % check_itm_code)
        abort(404)  # page not found

    if not request.json:
        current_app.logger.error('saveCheckResultAPI_view() function: Payload json must be set.')
        abort(400)  # bad request

    if state_updater.resultShouldBeNumerical():
        if not 'value' in request.json:
            current_app.logger.error('saveCheckResultAPI_view() function: value must be set.')
            abort(400)  # bad request
        else:
            value = request.json['value']

            detail_msg = request.json.get('detail_msg', "")
            notification_msg = request.json.get('notification_msg', "")
            state_updater.updateNumericalResult(value, detail_msg, notification_msg)
    else:
        if not request.json or not 'status' in request.json:
            abort(400)  # bad request
        else:
            status = request.json['status']
            detail_msg = request.json.get('detail_msg', "")
            notification_msg = request.json.get('notification_msg', "")
            state_updater.updateNonnumericalResult(status, detail_msg, notification_msg)

    return jsonify({'echo_msg': 'successful'}), 201


@mod.route("/api/v1.0/exceptions/<check_itm_code>", methods=('POST', 'GET'))
def registerExceptionAPI_view(check_itm_code):
    exception_msg = request.json.get('exception_msg', "No exception provided.")
    state_updater = JobStateUpdater(check_itm_code)
    if state_updater.isUndefinedCheckItem():
        exception_msg = "Check item %s not found. The original message: %s" % (check_itm_code, exception_msg)
    current_app.logger.error('registerExceptionAPI_view(), Exception message: %s' % exception_msg)
    state_updater.registerCheckingException(exception_msg)
    return jsonify({'echo_msg': 'successful'}), 201


#-----------------------------------------
# test api below
#-----------------------------------------


@mod.route("/api/v1.0/test/simple", methods=('GET', 'POST'))
def test_simple_view():
    return jsonify({'request.method': request.method, 'save_status': 'successful'}), 201


@mod.route("/api/v1.0/test/str_arg/<check_itm_code>", methods=('POST', 'GET'))
def test_str_argument_view(check_itm_code):
    abort(400)
    return jsonify({'request.method': request.method, 'item': check_itm_code, 'save_status': 'successful'}), 201


@mod.route("/api/v1.0/test/int_arg/<int:seq_no>", methods=('POST', 'GET'))
def test_int_argument_view(seq_no):
    return jsonify({'request.method': request.method, 'seq_no': seq_no, 'save_status': 'successful'}), 201


@mod.route("/api/v1.0/test/json_post/<check_itm_code>", methods=('POST', 'GET'))
def test_json_post_view(check_itm_code):
    if not request.json:
        abort(400)  # bad request

    if not 'value' in request.json:
        abort(400)  # bad request

    value = request.json['value']
    detail_msg = request.json.get('detail_msg', "")  # if detail_msg is not set, use empty
    return jsonify({'request.method': request.method, 'value': value, 'detail_msg': detail_msg, 'save_status': 'successful'}), 201
