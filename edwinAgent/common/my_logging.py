'''
Created on 2013-4-15
'''
import sys
import logging
from .os_helper import isWindows, isJython


# ConcurrentRotatingFileHandler is the best rotating file handler.
# Jython:  ConcurrentRotatingFileHandler does not support Jython.
#         Reason: pywin32 cannot work on windows, fcntl missed on linux
# Windows: If ConcurrentRotatingFileHandler does not install, use TimedRotatingFileHandler rather than RotatingFileHandler.
#         Reason: because RotatingFileHandler will fail when the file size is up to maxBytes on windows,
#                 And TimedRotatingFileHandler will fail if the log file is being written at 23:59
#                 But the chance of TimedRotatingFileHandler failure is less than RotatingFileHandler


root_logger = None
useRotatingFileHandler = True
if isJython():
    if isWindows():
        useRotatingFileHandler = False
        from logging.handlers import TimedRotatingFileHandler
    else:
        useRotatingFileHandler = True
        from logging.handlers import RotatingFileHandler as RFHandler
else:
    useRotatingFileHandler = True
    try:
        from ..site_packages.ConcurrentLogHandler084.cloghandler import ConcurrentRotatingFileHandler as RFHandler
    except ImportError, ex:
        print(ex)
        from warnings import warn
        warn("ConcurrentLogHandler package failed to import. Use built-in log handler instead.")
        if isWindows():
            useRotatingFileHandler = False
            from logging.handlers import TimedRotatingFileHandler
        else:
            useRotatingFileHandler = True
            from logging.handlers import RotatingFileHandler as RFHandler


def configureLogger(logger, log_file, log_level, console_ouput=True):
    '''
    Only the root logger need to configure.  
    '''
    # create RotatingFileHandler and set level to debug
    global root_logger
    root_logger = logger
    if (log_file is not None):
        print("log_file=%s" % (log_file))
        if useRotatingFileHandler:
            fh = RFHandler(filename=log_file, mode='a', maxBytes=10 * 1024 * 1024, backupCount=10, encoding='utf-8')
        else:
            fh = TimedRotatingFileHandler(filename=log_file, when='midnight', interval=1, backupCount=10, encoding='utf-8')

        formatter = logging.Formatter(fmt='%(asctime)s,pid=%(process)d,tid=%(thread)d,%(name)s,%(levelname)s:%(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.setLevel(log_level)

    # create consoleHanlder
    if (console_ouput):
        ch = logging.StreamHandler()
        shortFormatter = logging.Formatter(fmt='%(asctime)s,pid=%(process)d,tid=%(thread)d,%(name)s,%(levelname)s:%(message)s', datefmt="%H:%M:%S")
        ch.setFormatter(shortFormatter)
        logger.addHandler(ch)
        logger.setLevel(log_level)

    # catch the uncatched exception
    sys.excepthook = my_excepthook


def my_excepthook(exc_type, exc_value, exc_traceback):
    root_logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
