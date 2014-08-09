# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import
import time
import logging
import logging.config
from edwinServer.common import my_logging
from edwinServer.common import const
from edwinServer.common import conf
from edwinServer.common import os_helper
from edwinServer.common import database_all
from edwinServer.common.mail_service import MailSender
from edwinServer.common.model_meta import dashboard_check_log


# logging.basicConfig(level=logging.DEBUG)      # use for development
log_file = os_helper.getLoggingFileName(__file__)
root_logger = logging.getLogger()
my_logging.configureLogger(root_logger, log_file, conf.log_level)
logger = logging.getLogger(__name__)  # get current file logger


def check():
    logger.info("Get the alarm list need to send out.")
    alarms = dashboard_check_log.getAlarmSendList()

    alarmCount = len(alarms)
    logger.info("There are %d alarms totally." % (alarmCount))

    if alarms:
        mailSender = MailSender()
        for alarm in alarms:
            logger.info("---Begin to send alarm %s." % alarm)
            alarm.markSendAsStarted()

            logger.info("---To send alarm %s." % alarm)
            mailSender.send(alarm)

            sendStatus = const.ALARM_SEND_STATUS_SUCCESSFUL
            alarm.markSendAsFinished(sendStatus)
            logger.info("---End to send alarm %s." % alarm)
    database_all.closeAllConnections()


def main():
    in_daemon_mode = conf.alarm_send_in_daemon_mode
    if not in_daemon_mode:
        check()
    else:
        from apscheduler.scheduler import Scheduler
        minuteScheduler = Scheduler()
        sleep_seconds = 60  # just 60 seconds
        minuteScheduler.add_interval_job(check, seconds=sleep_seconds)
        minuteScheduler.start()
        while 1:
            time.sleep(9999)
        minuteScheduler.shutdown()


if __name__ == "__main__":
    logger.info("=================================")
    logger.info("===module: alarm_send")
    logger.info("=================================")

    main()

    logger.info("===End to run module: alarm_send")
