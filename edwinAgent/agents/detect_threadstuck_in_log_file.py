# -*- coding: utf-8 -*-
'''
to detect threadstuck fatel error in weblogic log file  
'''
from __future__ import absolute_import
import logging
import logging.config
from edwinAgent.common import const
from edwinAgent.common import conf
from edwinAgent.common import api_helper
from edwinAgent.common import os_helper
from edwinAgent.common import my_logging
from edwinAgent.site_packages.logwatch_glob import LogWatcher


# Must need Jython 2.7
# TODO: set in_dev_mode=True when application debug
in_dev_mode = False

app_server = "your_server"
file_pattern = "your_log_file.log"
log_folder = "/some_folder/some_file"
if in_dev_mode:
    log_folder = "c://"


# logging.basicConfig(level=logging.DEBUG)      # use for development
log_file = os_helper.getLoggingFileName(__file__)
root_logger = logging.getLogger()
my_logging.configureLogger(root_logger, log_file, conf.log_level)
logger = logging.getLogger(__name__)  # get current file logger


def logCaptureCallback(filename, lines):
    linesText = "".join(lines)
    logger.debug("Your log captured lines:%s" % linesText)

    index = linesText.find("[STUCK]")
    # Thread stuck issue happened
    if index >= 0:
        snippetIndex = index - 500
        snippet = linesText[max(0, snippetIndex):]
        status = const.CHECK_STATUS_CRITICAL
        detail_msg = """It seems your application hang on server %s. 
        We found [STUCK] word in log file %s. 
        -------- 
        Your log snippet:%s""" % (app_server, filename, snippet)
        logger.info(detail_msg)
        (successful, echo_msg) = api_helper.updateNonnumericalResult(itm_code, status, detail_msg)
        if successful:
            logger.info("update status successful.")
        else:
            logger.info("fail to update status. echo message: %s" % (echo_msg,))


def check():
    '''
    get check result, the result format is (status, detail_msg)
    '''
    includeSubFolder = False
    excludeFileListFile = None
    watcher = LogWatcher(log_folder, logCaptureCallback, file_pattern, includeSubFolder, excludeFileListFile, tail_lines=100)
    watcher.loop()


def main(itm_code):
    try:
        try:
            global state_updater
            (status, detail_msg) = check()
        except Exception, e:
            logger.exception(e)
            exception_msg = "%s" % e
            api_helper.registerException(itm_code, exception_msg)
        else:
            # Log capture is aborted, mark as warning
            status = const.CHECK_STATUS_WARN
            detail_msg = """On server %s, it is aborted to capture the log file (%s,%s).
              Then it will cause false alarm when next check.""" % (app_server, log_folder, file_pattern)
            logger.info("Check status: %s" % status)
            logger.info("Check detail message: %s" % detail_msg)
            api_helper.registerException(itm_code, detail_msg)

    except Exception, e:
        logger.exception(e)


if __name__ == "__main__":
    itm_code = "DETECT_THREADSTUCK_IN_LOG_FILE"  # configure this check item in your database before run
    logger.info("=================================")
    logger.info("===check item: %s" % itm_code)
    logger.info("=================================")

    main(itm_code)

    logger.info("===End to check: %s" % itm_code)
