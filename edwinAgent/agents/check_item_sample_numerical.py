# -*- coding: utf-8 -*-
'''
numerical checking item sample 
'''
from __future__ import absolute_import
import logging
import logging.config
from edwinAgent.common import const
from edwinAgent.common import conf
from edwinAgent.common import api_helper
from edwinAgent.common import os_helper
from edwinAgent.common import my_logging


# logging.basicConfig(level=logging.DEBUG)      # use for development
log_file = os_helper.getLoggingFileName(__file__)
root_logger = logging.getLogger()
my_logging.configureLogger(root_logger, log_file, conf.log_level)
logger = logging.getLogger(__name__)  # get current file logger


def check():
    '''
    get check result, format is (check_value, detail_msg, notification_msg)
    '''
    # TODO: get check_value and detail_msg by yourself.
    check_value = 10
    detail_msg = "some message here"
    notification_msg = "some notification message in your email"
    return (check_value, detail_msg, notification_msg)


def main(itm_code):
    try:
        try:
            (check_value, detail_msg, notification_msg) = check()
        except Exception, e:
            logger.exception(e)
            exception_msg = "%s" % e
            api_helper.registerException(itm_code, exception_msg)
        else:
            logger.info("Check value: %d" % check_value)
            logger.info("Check detail message: %s" % detail_msg)
            (successful, echo_msg) = api_helper.updateNumericalResult(itm_code, check_value, detail_msg, notification_msg)
            if successful:
                logger.info("update status successful.")
            else:
                logger.info("fail to update status. echo message: %s" % (echo_msg,))

    except Exception, e:
        logger.exception(e)


if __name__ == "__main__":
    itm_code = 'UNIT_TEST_NUMERICAL'
    logger.info("=================================")
    logger.info("===check item: %s" % itm_code)
    logger.info("=================================")

    main(itm_code)

    logger.info("===End to check: %s" % itm_code)
