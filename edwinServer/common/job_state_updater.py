# -*- coding: utf-8 -*-
'''

'''

from __future__ import absolute_import
import logging
from datetime import datetime
from .model_meta import dashboard_check_cfg, dashboard_check_log
from . import const


class JobStateUpdater(object):

    def __init__(self, itm_code):
        self.logger = logging.getLogger(__name__)
        self.logger.info('To update check result for %s' % itm_code)

        self.itm_code = itm_code
        self.check_cfg = dashboard_check_cfg.getCfgInDb(itm_code)
        self.logger.debug('Check item cfg object: %s' % (self.check_cfg))

    def isUndefinedCheckItem(self):
        return self.check_cfg is None

    def resultShouldBeNumerical(self):
        return self.check_cfg.check_value_is_number == 'Y'

    def updateNumericalResult(self, check_value, detail_msg, notification_msg=''):
        '''
        update check result for numeric check_item
        '''

        status = self._getStatusByValue(check_value)
        self._updateCheckResult(check_value, status, detail_msg, notification_msg)

    def updateNonnumericalResult(self, status, detail_msg, notification_msg=''):
        '''
        update check result for non-numeric check_item
        '''
        check_value = const.CHECK_VALUE_NA
        self._updateCheckResult(check_value, status, detail_msg, notification_msg)

    def registerCheckingException(self, exception_msg):
        '''
        Register checking exception. 
        It always generate one critical alarm in check item of CHECK_ITEM_BUILTIN_EXCEPTION_NOTIFY
        '''
        notifyJob = JobStateUpdater(const.CHECK_ITEM_BUILTIN_EXCEPTION_NOTIFY)
        status = const.CHECK_STATUS_CRITICAL
        detail_msg = "Check item %s has exception. Exception message: %s " % (self.itm_code, exception_msg)
        notifyJob.updateNonnumericalResult(status, detail_msg)

    def _getStatusByValue(self, check_value):
        '''
        get status according to check value and spec
        '''
        self.logger.debug("check_value_is_number=%s" % self.check_cfg.check_value_is_number)
        try:
            assert(self.check_cfg.check_value_is_number == 'Y')
        except Exception as ex:
            self.logger.exception("%s" % ex)
            raise ex
        result = const.CHECK_STATUS_NORMAL

        if self.check_cfg.smaller_is_better:
            if check_value >= self.check_cfg.critical_limit:
                result = const.CHECK_STATUS_CRITICAL
            elif check_value >= self.check_cfg.warning_limit:
                result = const.CHECK_STATUS_WARN
        else:
            if check_value <= self.check_cfg.critical_limit:
                result = const.CHECK_STATUS_CRITICAL
            elif check_value <= self.check_cfg.warning_limit:
                result = const.CHECK_STATUS_WARN

        return result

    def _updateCheckResult(self, check_value, status, detail_msg, notification_msg=''):
        '''
        update check result in cfg table and log table
        '''
        if self.check_cfg.enabled_flag != 'Y':
            self.logger.info('The check item %s is disable in database. So the coming result will be not stored anymore.' % (self.itm_code))
            return

        self.logger.info('check_value %s' % check_value)
        self.logger.info('check_status %s' % status)

        check_timestamp = datetime.now().strftime("%Y%m%d %H:%M:%S.%f")  # '%s'%datetime.now()
        try:
            assert(status in [const.CHECK_STATUS_NORMAL, const.CHECK_STATUS_WARN, const.CHECK_STATUS_CRITICAL])
        except Exception as ex:
            self.logger.exception(ex)
            raise ex

        # update status in check_item cfg table
        self.check_cfg.updateStatus(check_value, status, check_timestamp, detail_msg, notification_msg)

        is_critical_event = self.check_cfg.is_critical_event
        if is_critical_event == 'Y':
            self.logger.warn("The alarm is a critical level alarm.")
        is_warning_event = self.check_cfg.is_warning_event
        if is_warning_event == 'Y':
            self.logger.warn("The alarm is a warning level alarm.")

        is_new_critical_event = self.check_cfg.is_new_critical_event
        if is_new_critical_event == 'Y':
            self.logger.warn("The alarm is a new critical level alarm.")
        is_new_warning_event = self.check_cfg.is_new_warning_event
        if is_new_warning_event == 'Y':
            self.logger.warn("The alarm is a new warning level alarm.")

        check_log = dashboard_check_log()
        check_log.initCheckStatus(self.itm_code, check_timestamp, status, check_value,
                                  self.check_cfg.warning_limit, self.check_cfg.critical_limit,
                                  self.check_cfg.shadow_data, detail_msg, notification_msg,
                                  is_critical_event, is_warning_event,
                                  is_new_critical_event, is_new_warning_event)
        check_log.insertLog()
