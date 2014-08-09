# -*- coding: utf-8 -*-
'''
Created on 2014-2-10

'''
from __future__ import absolute_import
from flask import Blueprint, abort, request, flash, jsonify
from ...common.job_state_updater import JobStateUpdater


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


@mod.route("/api/v1.0/checks/<check_itm_code>", methods=('POST', 'GET'))
def saveCheckResultAPI_view(check_itm_code):
    state_updater = JobStateUpdater(check_itm_code)
    if state_updater.isUndefinedCheckItem():
        flash('Undefined check item %s.' % check_itm_code, 'error')
        abort(404)  # page not found

    if not request.json:
        abort(400)  # bad request

    if state_updater.resultShouldBeNumerical():
        if not 'value' in request.json:
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
    state_updater = JobStateUpdater(check_itm_code)
    if state_updater.isUndefinedCheckItem():
        # abort(404)  # check item not found
        return jsonify({'echo_msg': 'Check item %s not found' % (check_itm_code)}), 400

    if not request.json:
        # abort(400)  # bad request
        return jsonify({'echo_msg': 'Request json data not found'}), 400

    if not 'exception_msg' in request.json:
        # abort(400)  # bad request
        return jsonify({'echo_msg': 'No exception_msg in the request json data'}), 400
    else:
        exception_msg = request.json.get('exception_msg', "")
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
