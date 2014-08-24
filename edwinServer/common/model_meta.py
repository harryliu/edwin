# -*- coding: utf-8 -*-
'''
DAL of edwin database 
'''
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import unicode_literals
import logging
from datetime import datetime, timedelta
from ..site_packages.dbRowFactory.pyDbRowFactory import DbRowFactory
from . import database_meta
from . import const


def executeSqlWithLog(cursor, sql, params=None):
    logger = logging.getLogger(__name__)
    logger.debug('===SQL statement is:')
    logger.debug(sql)
    if params is not None and params.__len__() > 0:
        logger.debug('---SQL parameter list BEGIN:')
        for param in params:
            logger.debug('%s' % param)
        logger.debug('---SQL parameter list END.')
    cursor.execute(sql, params)


class dashboard_page(object):
    FULL_NAME = 'edwinServer.common.model_meta.dashboard_page'
    TABLE_NAME = 'EDWIN_PAGE'
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.page_code = ""
        self.page_title = ""
        self._display_flag = "Y"   # Y/N
        self.description = ""

    @property
    def display_flag(self):
        if self._display_flag in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @display_flag.setter
    def display_flag(self, value):
        self._display_flag = value

    @classmethod
    def getOnePage(cls, page_code):
        cls.logger.info("Query DB to get configuration for page %s" % (page_code))

        sql = """
            select * from EDWIN_PAGE
            where 1=1
            and page_code=?
            """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (page_code,))
            if cr.rowcount == 0:
                return None
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                row = rowFactory.fetchOneRowObject()
                return row

    @classmethod
    def getAllPages(cls, including_hiden=False):
        cls.logger.info("Query DB to get all pages configuration.")

        if including_hiden:
            sql = """
                select * from EDWIN_PAGE
                WHERE 1=1
                ORDER BY page_title, page_code
                """
        else:
            sql = """
                select * from EDWIN_PAGE
                WHERE 1=1
                AND display_flag='Y'
                ORDER BY page_title, page_code
                """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, )
            if cr.rowcount == 0:
                return []
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                rows = rowFactory.fetchAllRowObjects()
                return rows


class dashboard_pagelet(object):
    FULL_NAME = 'edwinServer.common.model_meta.dashboard_pagelet'
    TABLE_NAME = 'EDWIN_PAGELET'
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.pagelet_code = ""
        self.pagelet_title = ""
        self.page_code = ""
        self.display_order = 0
        self._display_flag = "Y"   # Y/N
        self.description = ""

    @property
    def display_flag(self):
        if self._display_flag in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @display_flag.setter
    def display_flag(self, value):
        self._display_flag = value

    @classmethod
    def getOnePagelet(cls, pagelet_code):
        cls.logger.info("Query DB to get pagelet configuration.")

        sql = """
            select * from EDWIN_PAGELET
            where 1=1
            and pagelet_code=?
            """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (pagelet_code,))
            if cr.rowcount == 0:
                return None
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                row = rowFactory.fetchOneRowObject()
                return row

    @classmethod
    def getAllPagelets(cls, page_code):
        cls.logger.info("Query DB to get all pagelets under page %s ." % (page_code))

        sql = """
            select * from EDWIN_PAGELET
            where 1=1
            and PAGE_CODE=?
            and DISPLAY_FLAG='Y'
            order by DISPLAY_ORDER, PAGELET_TITLE
            """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (page_code,))
            if cr.rowcount == 0:
                return []
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                rows = rowFactory.fetchAllRowObjects()
                return rows

    def getCheckItems(self):
        self.logger.info("Query DB to get check list under pagelet %s ." % (self.pagelet_code))

        sql = """
            select c.itm_code from edwin_pagelet_check_list p
            join  EDWIN_CHECK_ITM_CFG c on  p.check_itm_code=c.itm_code
            where 1=1
            and p.display_flag='Y'
            and c.enabled_flag='Y'
            and p.pagelet_code=?
            order by p.display_order, c.itm_title  
            """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (self.pagelet_code,))
            rows = cr.fetchall()
            result = []
            for row in rows:
                result.append(dashboard_check_cfg.getCfgInDb(row[0]))

        return result


class dashboard_check_cfg(object):
    FULL_NAME = 'edwinServer.common.model_meta.dashboard_check_cfg'
    TABLE_NAME = 'EDWIN_CHECK_ITM_CFG'
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.itm_code = ""
        self.itm_title = ""
        self.itm_category = ""
        self._enabled_flag = ""   # Y/N
        self.host = ""   # just for reference, this application will not call the script
        self.check_script = ""   # just for reference, this application will not call the script
        self.check_interval_minute = ""
        self._check_value_is_number = ""   # Y/N
        self.description = ""
        self.warning_limit = ""
        self.critical_limit = ""
        self.shadow_data = ""   # shadow_data will copy to EDWIN_CHECK_ITM_LOG table
        self.owner_team_list = ""
        self.warning_mail_cc = ""
        self.critical_mail_cc = ""
        self._critical_sms_flag = ""    # Y/N
        self._critical_call_flag = ""    # Y/N
        self._allow_repeated_sms_alarm = ""    # Y/N
        self._allow_repeated_call_alarm = ""    # Y/N
        self._allow_repeated_mail_alarm = ""    # Y/N
        self.last_check_timestamp = ""
        self.last_status = ""
        self.last_value = ""
        self.last_detail_msg = ""
        self.last_notification_msg = ""
        self._is_critical_event = ""    # Y/N
        self._is_warning_event = ""    # Y/N
        self._is_new_critical_event = ""    # Y/N
        self._is_new_warning_event = ""    # Y/N

    @property
    def enabled_flag(self):
        if self._enabled_flag in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @enabled_flag.setter
    def enabled_flag(self, value):
        self._enabled_flag = value

    @property
    def check_value_is_number(self):
        if self._check_value_is_number in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @check_value_is_number.setter
    def check_value_is_number(self, value):
        self._check_value_is_number = value

    @property
    def critical_sms_flag(self):
        if self._critical_sms_flag in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @critical_sms_flag.setter
    def critical_sms_flag(self, value):
        self._critical_sms_flag = value

    @property
    def critical_call_flag(self):
        if self._critical_call_flag in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @critical_call_flag.setter
    def critical_call_flag(self, value):
        self._critical_call_flag = value

    @property
    def allow_repeated_sms_alarm(self):
        if self._allow_repeated_sms_alarm in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @allow_repeated_sms_alarm.setter
    def allow_repeated_sms_alarm(self, value):
        self._allow_repeated_sms_alarm = value

    @property
    def allow_repeated_call_alarm(self):
        if self._allow_repeated_call_alarm in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @allow_repeated_call_alarm.setter
    def allow_repeated_call_alarm(self, value):
        self._allow_repeated_call_alarm = value

    @property
    def allow_repeated_mail_alarm(self):
        if self._allow_repeated_mail_alarm in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @allow_repeated_mail_alarm.setter
    def allow_repeated_mail_alarm(self, value):
        self._allow_repeated_mail_alarm = value

    @property
    def is_new_critical_event(self):
        if self._is_new_critical_event in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @is_new_critical_event.setter
    def is_new_critical_event(self, value):
        self._is_new_critical_event = value

    @property
    def is_new_warning_event(self):
        if self._is_new_warning_event in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @is_new_warning_event.setter
    def is_new_warning_event(self, value):
        self._is_new_warning_event = value

    @property
    def is_critical_event(self):
        if self._is_critical_event in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @is_critical_event.setter
    def is_critical_event(self, value):
        self._is_critical_event = value

    @property
    def is_warning_event(self):
        if self._is_warning_event in ['Y', 'y', 'T', 't']:
            return 'Y'
        else:
            return 'N'

    @is_warning_event.setter
    def is_warning_event(self, value):
        self._is_warning_event = value

    @property
    def smaller_is_better(self):
        result = True  # check spec trend
        if self.check_value_is_number:
            if self.critical_limit < self.warning_limit:
                result = False
        return result

    @property
    def is_outdated(self):
        '''
        check the last checking is out of date?
        '''
        return self.check_outdated(self.check_interval_minute, self.last_check_timestamp)

    @classmethod
    def check_outdated(cls, check_interval_minute, last_check_timestamp):
        '''
        check the last checking is out of date?
        '''
        if check_interval_minute <= 0:
            return False
        elif last_check_timestamp is None:
            return False
        else:
            last = datetime.strptime(last_check_timestamp, "%Y%m%d %H:%M:%S.%f")
            delta = timedelta(minutes=check_interval_minute)
            now = datetime.now()
            return now > (last + delta)

    @classmethod
    def getAllChkItems(cls):
        cls.logger.info("Query DB to get all check items configuration.")

        sql = """
            select c.*
                ,s.LAST_CHECK_TIMESTAMP      
                ,s.LAST_STATUS               
                ,s.LAST_VALUE                
                ,s.LAST_DETAIL_MSG
                ,s.LAST_NOTIFICATION_MSG                  
                ,s.IS_WARNING_EVENT          
                ,s.IS_CRITICAL_EVENT         
                ,s.IS_NEW_CRITICAL_EVENT     
                ,s.IS_NEW_WARNING_EVENT                  
             from EDWIN_CHECK_ITM_CFG c
             left join EDWIN_CHECK_ITM_STATUS s on c.ITM_CODE=s.ITM_CODE
             WHERE 1=1
             order by  c.itm_title 
            """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, )
            if cr.rowcount == 0:
                return []
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                rows = rowFactory.fetchAllRowObjects()
                return rows

    @classmethod
    def getCfgInDb(cls, itm_code):
        cls.logger.info("Query DB to get check item configuration.")

        sql = """
            select c.*
                ,s.LAST_CHECK_TIMESTAMP      
                ,s.LAST_STATUS               
                ,s.LAST_VALUE                
                ,s.LAST_DETAIL_MSG   
                ,s.LAST_NOTIFICATION_MSG                
                ,s.IS_WARNING_EVENT          
                ,s.IS_CRITICAL_EVENT         
                ,s.IS_NEW_CRITICAL_EVENT     
                ,s.IS_NEW_WARNING_EVENT                  
             from EDWIN_CHECK_ITM_CFG c
             left join EDWIN_CHECK_ITM_STATUS s on c.ITM_CODE=s.ITM_CODE
             WHERE 1=1
             and c.itm_code=?
             order by  c.itm_title             
            """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (itm_code,))
            if cr.rowcount == 0:
                return None
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                row = rowFactory.fetchOneRowObject()
				if row:
					if row.warning_mail_cc is None:
						row.warning_mail_cc = ""
					if row.critical_mail_cc is None:
						row.critical_mail_cc = ""
                return row

    def updateStatus(self, check_value, check_status, check_timestamp, detail_msg, notification_msg=''):
        self.logger.info("Update check status in check_cfg table.")

        self.last_check_timestamp = check_timestamp
        self.last_status = check_status
        self.last_value = check_value
        self.last_detail_msg = detail_msg
        self.last_notification_msg = notification_msg
        if self.last_value == const.CHECK_VALUE_NA:
            self.last_value = None

        # check if new critical or warning alarm
        if self.itm_code == const.CHECK_ITEM_BUILTIN_EXCEPTION_NOTIFY:
            if check_status == const.CHECK_STATUS_CRITICAL:
                self.is_new_critical_event = 'Y'
            else:
                self.is_new_critical_event = 'N'
        else:
            if check_status == const.CHECK_STATUS_CRITICAL and self.is_critical_event != 'Y':  # check last status
                self.is_new_critical_event = 'Y'
            else:
                self.is_new_critical_event = 'N'

        if self.itm_code == const.CHECK_ITEM_BUILTIN_EXCEPTION_NOTIFY:
            if check_status == const.CHECK_STATUS_WARN:
                self.is_new_warning_event = 'Y'
            else:
                self.is_new_warning_event = 'N'
        else:
            if check_status == const.CHECK_STATUS_WARN and self.is_warning_event != 'Y':  # check last status
                self.is_new_warning_event = 'Y'
            else:
                self.is_new_warning_event = 'N'

        # Set status for this event
        self.is_critical_event = 'N'
        self.is_warning_event = 'N'
        if check_status == const.CHECK_STATUS_CRITICAL:
            self.is_critical_event = 'Y'
        elif check_status == const.CHECK_STATUS_WARN:
            self.is_warning_event = 'Y'

        if self.itm_code == const.CHECK_ITEM_BUILTIN_EXCEPTION_NOTIFY:
            if check_status == const.CHECK_STATUS_WARN:
                self.is_new_warning_event = 'Y'
            else:
                self.is_new_warning_event = 'N'

        sql_delete = """DELETE FROM EDWIN_CHECK_ITM_STATUS S
            where 1=1
            and S.ITM_CODE=?
        """
        sql_insert = """INSERT INTO EDWIN_CHECK_ITM_STATUS
            (ITM_CODE,LAST_CHECK_TIMESTAMP,LAST_STATUS,LAST_VALUE,LAST_DETAIL_MSG,LAST_NOTIFICATION_MSG,
             IS_CRITICAL_EVENT,IS_WARNING_EVENT,IS_NEW_CRITICAL_EVENT,IS_NEW_WARNING_EVENT) 
          VALUES 
            (?,?,?,?,?,?,
            ?,?,?,?)
          """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql_delete, (self.itm_code,))
            executeSqlWithLog(cr, sql_insert, (self.itm_code,
                                               self.last_check_timestamp,
                                               self.last_status,
                                               self.last_value,
                                               self.last_detail_msg,
                                               self.last_notification_msg,
                                               self.is_critical_event,
                                               self.is_warning_event,
                                               self.is_new_critical_event,
                                               self.is_new_warning_event,
                                               ))
            conn.commit()


class dashboard_check_log(object):
    FULL_NAME = 'edwinServer.common.model_meta.dashboard_check_log'
    TABLE_NAME = 'EDWIN_CHECK_ITM_LOG'
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.itm_code = ""
        self.check_timestamp = ""
        self.check_status = ""
        self.check_value = ""
        self.check_detail_msg = ""
        self.check_notification_msg = ""
        self.check_date = ""
        self.warning_limit = ""
        self.critical_limit = ""
        self.shadow_data = ""
        self.is_critical_event = ""
        self.is_warning_event = ""
        self.is_new_critical_event = ""
        self.is_new_warning_event = ""
        self.alarm_send_status = ""
        self.alarm_send_begin_time = ""
        self.alarm_send_end_time = ""

    def __str__(self):
        return "[%s; %s]" % (self.itm_code, self.check_timestamp)

    def initCheckStatus(self, itm_code, check_timestamp, check_status, check_value,
                        warning_limit, critical_limit,
                        shadow_data, check_detail_msg, check_notification_msg,
                        is_critical_event, is_warning_event,
                        is_new_critical_event, is_new_warning_event):
        self.itm_code = itm_code
        self.check_timestamp = check_timestamp   # 20140117 16:20:27.783999
        self.check_status = check_status
        self.check_value = check_value
        self.warning_limit = warning_limit
        self.critical_limit = critical_limit
        self.shadow_data = shadow_data
        self.check_detail_msg = check_detail_msg
        self.check_notification_msg = check_notification_msg
        self.check_date = self.check_timestamp[0:8]  # 20140114
        self.is_critical_event = is_critical_event
        self.is_warning_event = is_warning_event
        self.is_new_critical_event = is_new_critical_event
        self.is_new_warning_event = is_new_warning_event

        if self.is_critical_event == 'Y' or self.is_warning_event == 'Y':
            self.alarm_send_status = const.ALARM_SEND_STATUS_WAITING
        else:
            self.alarm_send_status = const.ALARM_SEND_STATUS_NA

        self.alarm_send_begin_time = ''
        self.alarm_send_end_time = ''

        if self.check_value == const.CHECK_VALUE_NA:
            self.check_value = None

    @classmethod
    def getAlarmSendList(cls):
        '''
        get the alarm list need to send out 
        '''
        cls.logger.info("Get the alarm list to send out.")

        sql = """
        select * from EDWIN_CHECK_ITM_LOG 
        where 1=1
        and (IS_CRITICAL_EVENT='Y' OR IS_WARNING_EVENT='Y')
        and ALARM_SEND_STATUS=?
        order by CHECK_TIMESTAMP 
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (const.ALARM_SEND_STATUS_WAITING,))
            if cr.rowcount == 0:
                return []
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                return rowFactory.fetchAllRowObjects()

    def markSendAsStarted(self):
        '''
        mark alarm sending as started
        '''
        self.logger.info("Mark the alarm sending as started for alarm %s." % self)

        self.alarm_send_begin_time = '%s' % datetime.now()
        self.alarm_send_status = const.ALARM_SEND_STATUS_SENDING
        sql = """
        update edwin_check_itm_log 
        set alarm_send_status=?
        ,alarm_send_begin_time=?
        where 1=1
        and itm_code=?
        and check_timestamp=?
        and (is_critical_event='Y' or is_warning_event='Y')
        and alarm_send_status=?
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (self.alarm_send_status,
                                        self.alarm_send_begin_time,
                                        self.itm_code,
                                        self.check_timestamp,
                                        const.ALARM_SEND_STATUS_WAITING
                                        ))
            conn.commit()

    def markSendAsFinished(self, sendStatus):
        '''
        mark alarm sending as finished
        '''
        self.logger.info("Mark the alarm sending as finished for alarm %s." % self)

        try:
            assert(sendStatus in [const.ALARM_SEND_STATUS_FAILED, const.ALARM_SEND_STATUS_SUCCESSFUL])
        except Exception as ex:
            self.logger.exception(ex)
            raise ex
        self.alarm_send_end_time = '%s' % datetime.now()
        self.alarm_send_status = sendStatus
        sql = """
        update edwin_check_itm_log 
        set alarm_send_status=?
        ,alarm_send_end_time=?
        where 1=1
        and itm_code=?
        and check_timestamp=?
        and (is_critical_event='Y' or is_warning_event='Y')
        and alarm_send_status=?
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (self.alarm_send_status,
                                        self.alarm_send_end_time,
                                        self.itm_code,
                                        self.check_timestamp,
                                        const.ALARM_SEND_STATUS_SENDING
                                        ))
            conn.commit()

    def insertLog(self):
        self.logger.info("Insert check status in log table")

        sql = """
        insert into EDWIN_CHECK_ITM_LOG
        (itm_code,check_date,check_timestamp,
        check_status,check_value,
        warning_limit,critical_limit,
        shadow_data,check_detail_msg,check_notification_msg, 
        is_critical_event,is_warning_event, 
        is_new_critical_event,is_new_warning_event,
        alarm_send_status)
        values
        (?,?,?,
         ?,?,
         ?,?,
         ?,?,?,
         ?,?,
         ?,?,
         ?
         )
        """

        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (self.itm_code,
                                        self.check_date,
                                        self.check_timestamp,
                                        self.check_status,
                                        self.check_value,
                                        self.warning_limit,
                                        self.critical_limit,
                                        self.shadow_data,
                                        self.check_detail_msg,
                                        self.check_notification_msg,
                                        self.is_critical_event,
                                        self.is_warning_event,
                                        self.is_new_critical_event,
                                        self.is_new_warning_event,
                                        self.alarm_send_status
                                        ))
            conn.commit()


class CheckItemStatistics(object):

    '''
    get item checking statistics in time line
    '''

    logger = logging.getLogger(__name__)

    def __init__(self, check_item_obj):
        self.check_item = check_item_obj
        self.long_term_day_count = 31 * 4
        self.long_term_month_count = 4
        self.short_term_day_count = 31
        self.short_term_month_count = 1
        self.itm_code = self.check_item.itm_code

    def _getStatusData(self, is_short_term=True):
        self.logger.info("Get status statistics of the given check item .")

        if is_short_term:
            term_day_count = self.short_term_day_count
            term_month_count = self.short_term_month_count
        else:
            term_day_count = self.long_term_day_count
            term_month_count = self.long_term_month_count
        now = datetime.now()
        to_date = now.strftime("%Y%m%d")
        from_date = (now + timedelta(days=-1 * term_day_count)).strftime("%Y%m%d")
        itm_code = self.itm_code

        sql = """
            select d.date_id, l3.normal_count, l3.warning_count, l3.critical_count  
              from edwin_calendar_day d left join 
              (   select check_date, sum(normal_count) normal_count, sum(warning_count) warning_count, 
                   sum(critical_count) critical_count 
                 from
                (
                    select l.check_date, count(*) normal_count, 0 warning_count, 0 critical_count  
                      from edwin_check_itm_log l 
                      where 1=1
                      and l.itm_code=?
                      and l.check_status='NORMAL'
                      and l.check_date>=?
                      group by l.check_date
                    union all 
                    select l.check_date, 0 normal_count, count(*)  warning_count, 0 critical_count  
                      from edwin_check_itm_log l 
                      where 1=1
                      and l.itm_code=?
                      and l.check_status='WARNING'
                      and l.check_date>=?
                      group by l.check_date
                    union all
                    select l.check_date, 0 normal_count, 0 warning_count, count(*) critical_count  
                      from edwin_check_itm_log l 
                      where 1=1
                      and l.itm_code=?
                      and l.check_status='CRITICAL'
                      and l.check_date>=?
                      group by l.check_date 
                 ) l2  
                group by l2.check_date
              ) l3
           on l3.check_date=d.date_id
           where 1=1
           and d.date_id>=?
           and d.date_id<=?
           order by d.date_id   
        """
        date_list = []
        normal_list = []
        warning_list = []
        critical_list = []
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (itm_code, from_date,
                                        itm_code, from_date,
                                        itm_code, from_date,
                                        from_date, to_date))
            rows = cr.fetchall()
            for row in rows:
                date_list.append(row[0])
                normal_list.append(row[1])
                warning_list.append(row[2])
                critical_list.append(row[3])

        result = [date_list, normal_list, warning_list, critical_list, term_month_count]
        return result

    def _getValueData(self, is_short_term=True):
        self.logger.info("Get value statistics of the given check item .")

        if is_short_term:
            term_day_count = self.short_term_day_count
            term_month_count = self.short_term_month_count
        else:
            term_day_count = self.long_term_day_count
            term_month_count = self.long_term_month_count

        now = datetime.now()
        to_date = now.strftime("%Y%m%d")
        from_date = (now + timedelta(days=-1 * term_day_count)).strftime("%Y%m%d")
        itm_code = self.itm_code

        sql = """
            select d.date_id, l2.avg_value, l2.min_value, l2.max_value, 
               l2.warning_limit, l2.critical_limit  from edwin_calendar_day d 
            left join 
            (    
              select l.check_date, avg(l.check_value) avg_value, min(l.check_value) min_value, 
                  max(l.check_value) max_value, l.warning_limit, l.critical_limit  
                from edwin_check_itm_log l
                where 1=1
                and l.itm_code=?
                and l.check_date>=?
                group by l.check_date, l.warning_limit, l.critical_limit
            ) l2
           on l2.check_date=d.date_id
           where 1=1
           and d.date_id>=?
           and d.date_id<=?
           order by d.date_id 
        """
        date_list = []
        avg_value_list = []
        min_value_list = []
        max_value_list = []
        warning_limit_list = []
        critical_limit_list = []
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (itm_code, from_date,
                                        from_date, to_date))
            rows = cr.fetchall()
            for row in rows:
                date_list.append(row[0])
                avg_value_list.append(row[1])
                min_value_list.append(row[2])
                max_value_list.append(row[3])
                warning_limit_list.append(row[4])
                critical_limit_list.append(row[5])
        result = [date_list, avg_value_list, min_value_list, max_value_list, warning_limit_list, critical_limit_list, term_month_count]
        return result

    def getShortTermValueData(self):
        return self._getValueData(is_short_term=True)

    def getLongTermValueData(self):
        return self._getValueData(is_short_term=False)

    def getShortTermStatusData(self):
        return self._getStatusData(is_short_term=True)

    def getLongTermStatusData(self):
        return self._getStatusData(is_short_term=False)


class Summary(object):

    '''
    Show status statistics for page/pagelet  
    '''

    logger = logging.getLogger(__name__)

    def __init__(self, summary_code, summary_title, normal_count, outdated_count, warning_count, critical_count):
        self.summary_code = summary_code
        self.summary_title = summary_title  # summary_title.decode('gbk','ingore')
        self.total_count = int(normal_count + outdated_count + warning_count + critical_count)
        self.normal_count = int(normal_count)
        self.outdated_count = int(outdated_count)
        self.warning_count = int(warning_count)
        self.critical_count = int(critical_count)
        self.summary_status = self.refresh_summary_status()

    def refresh_summary_status(self):
        if self.critical_count > 0:
            self.summary_status = const.SUMMARY_STATUS_CRITICAL
        elif self.warning_count > 0:
            self.summary_status = const.SUMMARY_STATUS_WARNING
        elif self.outdated_count > 0:
            self.summary_status = const.SUMMARY_STATUS_OUTDATED
        else:
            self.summary_status = const.SUMMARY_STATUS_NORMAL

    @staticmethod
    def _is_outdated_check(row):
        '''
        judge the checking is outdated or not? 

        1. for page, the row format is [p.page_code, p.page_title, ck.check_interval_minute, ck.last_check_timestamp] 
        2. for pagelet, the row format is [p.pagelet_code, p.pagelet_title, ck.check_interval_minute, ck.last_check_timestamp]
        '''
        return dashboard_check_cfg.check_outdated(row[2], row[3])

    @classmethod
    def get_all_pages_summary(cls):
        '''
        get check items status under every page
        '''
        cls.logger.info("Get check items status under every page.")

        sql = """
         select p.page_code, p.page_title                
            ,sum(case  WHEN ck.last_status ='NORMAL' THEN 1 ELSE 0 END )  ROUGH_NORMAL_COUNT
            ,sum(case  WHEN ck.last_status ='WARNING' THEN 1 ELSE 0 END )  WARNING_COUNT
            ,sum(case  WHEN ck.last_status ='CRITICAL' THEN 1 ELSE 0 END )  CRITICAL_COUNT 
            from edwin_page p 
            left join edwin_pagelet pl on p.page_code=pl.page_code and pl.display_flag='Y'
            left join edwin_pagelet_check_list cl on pl.pagelet_code=cl.pagelet_code and cl.display_flag='Y'
            left join edwin_check_itm_cfg cfg on cfg.itm_code=cl.check_itm_code and cfg.enabled_flag='Y'
            left join edwin_check_itm_status ck on ck.itm_code=cfg.itm_code  
            where 1=1
            and p.display_flag='Y'
            GROUP BY p.page_code, p.page_title                
            order by p.page_code, p.page_title
        """

        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql,)
            rows = cr.fetchall()
            result = []
            for row in rows:
                result.append(Summary(row[0], row[1], row[2], 0, row[3], row[4]))

        # distinguish outdated_count from normal_count
        sql2 = """
        select p.page_code, p.page_title, cfg.check_interval_minute, ck.last_check_timestamp                        
            from edwin_page p 
            join edwin_pagelet pl on p.page_code=pl.page_code 
            join edwin_pagelet_check_list cl on pl.pagelet_code=cl.pagelet_code            
            join edwin_check_itm_cfg cfg on cfg.itm_code=cl.check_itm_code
            join edwin_check_itm_status ck on ck.itm_code=cl.check_itm_code
            where 1=1
            and p.display_flag='Y'
            and pl.display_flag='Y'
            and cl.display_flag='Y'
            and cfg.enabled_flag='Y'                
            and ck.last_status='NORMAL' 
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql2,)
            rows = cr.fetchall()
            outdated_rows = filter(cls._is_outdated_check, rows)

        for s in result:
            s.outdated_count = len([page for page in outdated_rows if page[0] == s.summary_code])
            s.normal_count = s.normal_count - s.outdated_count
            s.refresh_summary_status()

        return result

    @classmethod
    def get_all_pagelets_summmary(cls, page_code):
        '''
        get check items status under the given page
        '''
        cls.logger.info("Get check items status under the given page.")

        sql = """
        select pl.pagelet_code, pl.pagelet_title, pl.display_order 
        ,sum(case  WHEN ck.last_status ='NORMAL' THEN 1 ELSE 0 END )  ROUGH_NORMAL_COUNT
        ,sum(case  WHEN ck.last_status ='WARNING' THEN 1 ELSE 0 END )  WARNING_COUNT                         
        ,sum(case  WHEN ck.last_status ='CRITICAL' THEN 1 ELSE 0 END )  CRITICAL_COUNT
        from edwin_page p 
        join edwin_pagelet pl on p.page_code=pl.page_code and  pl.display_flag='Y'
        join edwin_pagelet_check_list cl on pl.pagelet_code=cl.pagelet_code and cl.display_flag='Y'
        join edwin_check_itm_cfg cfg on cfg.itm_code=cl.check_itm_code and cfg.enabled_flag='Y'
        left join edwin_check_itm_status ck on ck.itm_code=cfg.itm_code
        where 1=1           
        and p.page_code=?
        GROUP BY pl.pagelet_code, pl.pagelet_title, pl.display_order
        order by pl.display_order, pl.pagelet_title
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (page_code,))
            rows = cr.fetchall()
            result = []
            for row in rows:
                result.append(Summary(row[0], row[1], row[3], 0, row[4], row[5]))

        # exclude outdated_count from normal_count
        sql2 = """
        select pl.pagelet_code, pl.pagelet_title, cfg.check_interval_minute, ck.last_check_timestamp
        from  edwin_page p 
        join edwin_pagelet pl on p.page_code=pl.page_code 
        join edwin_pagelet_check_list cl on pl.pagelet_code=cl.pagelet_code
        join edwin_check_itm_cfg cfg on cfg.itm_code=cl.check_itm_code
        join edwin_check_itm_status ck on ck.itm_code=cl.check_itm_code
        where 1=1 
        and pl.display_flag='Y'
        and cl.display_flag='Y'
        and cfg.enabled_flag='Y'
        and ck.last_status='NORMAL'
        and p.page_code=?
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql2, (page_code,))
            rows = cr.fetchall()
            outdated_rows = filter(cls._is_outdated_check, rows)

        for s in result:
            s.outdated_count = len([pagelet for pagelet in outdated_rows if pagelet[0] == s.summary_code])
            s.normal_count = s.normal_count - s.outdated_count
            s.refresh_summary_status()

        return result


class team_mail_cfg(object):
    FULL_NAME = 'edwinServer.common.model_meta.team_mail_cfg'
    TABLE_NAME = 'EDWIN_TEAM_CFG'  # edw_mnt_alarm_mail_cfg
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.owner_team_code = ""
        self.email_to_list = ""
        self.sms_mail_to = ""
        self.sms_mail_title = ""
        self.phone_mail_to = ""
        self.phone_mail_title = ""

    @classmethod
    def getCfgInDb(cls, owner_team_code):
        sql = """
        select * from EDWIN_TEAM_CFG 
        where 1=1
        and  owner_team_code=?
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql, (owner_team_code,))
            if cr.rowcount == 0:
                return None
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                return rowFactory.fetchOneRowObject()

    @classmethod
    def getAllCfgInDb(cls):
        sql = """
        select * from EDWIN_TEAM_CFG 
        where 1=1 
        """
        conn = database_meta.openConnection()
        with conn.cursor() as cr:
            executeSqlWithLog(cr, sql,)
            if cr.rowcount == 0:
                return []
            else:
                rowFactory = DbRowFactory(cr, cls.FULL_NAME)
                return rowFactory.fetchAllRowObjects()
