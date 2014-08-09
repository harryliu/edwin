# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import with_statement
import os
import platform
import subprocess
import socket
from datetime import datetime
import time


def getIpAddr():
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr


def getHostName():
    return platform.node()


def isJython():
    return (platform.platform().find('Java') >= 0)


def isWindows():
    '''
    remark: sys.platform and os.name cannot identify in Jython, so use platform.platform()
    '''
    return (platform.platform().find('Windows') >= 0)


def isLinux():
    '''
    remark: sys.platform and os.name cannot identify in Jython, so use platform.platform()
    '''
    return (platform.platform().find('Linux') >= 0)


def isMac():
    '''
    remark: sys.platform and os.name cannot identify in Jython, so use platform.platform()
    '''
    plat = platform.platform()
    return (plat.find('Darwin') >= 0) or (plat.find('MacOS') >= 0)


def isPosix():
    if isJython() == False:
        return os.name == 'posix'
    elif isWindows():
        return False
    elif isMac():
        return False
    else:
        return True


def getNewLineSeperator():
    if isWindows():
        return '\r\n'
    elif isMac():
        return '\r'
    else:
        return '\n'


def launchCmdLine(*popenargs, **kwargs):
    '''
    run command line, return process object
    '''
    # capture cmd output
    # For windows, shell should be False, but there is a bug to run cmd.exe built-in command.  http://bugs.python.org/issue8224, we have to set shell=True
    # For Linux, shell=True
    if isWindows():
        shellValue = True
    else:
        shellValue = True

    process = subprocess.Popen(shell=shellValue, stdout=subprocess.PIPE, stderr=subprocess.PIPE, *popenargs, **kwargs)
    return process


def waitResultOfCmdProcess(process):
    '''
    check process result, return exitcode, output, error message together
    '''
    output, error = process.communicate()
    exitcode = process.wait()
    return (exitcode, output, error)


def waitAndLogResultOfCmdProcess(process, logFile, processStartTime=None):
    '''
    check process result,
    and then save  output, error message together to log file,
    return exitcode
    '''
    (exitcode, output, error) = waitResultOfCmdProcess(process)

    if logFile is not None:
        newlines = getNewLineSeperator()
        with open(logFile, "w") as f:
            f.write("---process id: %d" % process.pid)
            f.write(newlines)

            if processStartTime is not None:
                f.write("---started at: %s" % processStartTime)
                f.write(newlines)

            f.write("---ended at: %s" % datetime.now())
            f.write(newlines)

            f.write("---exit code: %d" % exitcode)
            f.write(newlines)

            f.write("---error message: ")
            f.write(newlines)
            f.write(error)
            f.write(newlines)

            f.write("---output message: ")
            f.write(newlines)
            f.write(output)
            f.write(newlines)

            f.close()
    return exitcode


def getFileLastModifiyTime(fname):
    mtime = time.ctime(os.stat(fname).st_mtime)
    tim = datetime.strptime(mtime[8:], "%d %H:%M:%S %Y")
    return tim


def getPath(fullFileName):
    '''
    c://1  ->  c:\\1

    '''
    (dirName, unused) = os.path.split(fullFileName)
    return os.path.normpath(dirName)


def getPathAndFileName(fullFileName):
    '''
    return (path, fileName)
    '''
    (dirName, fileName) = os.path.split(fullFileName)
    return (os.path.normpath(dirName), fileName)


def getLoggingFileName(py_main_file, log_short_path='logs'):
    (base_path, py_file_name) = getPathAndFileName(py_main_file)
    log_path = os.path.join(base_path, log_short_path)
    (log_short_name, ext) = os.path.splitext(py_file_name)
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    return os.path.join(log_path, log_short_name + '.log')


def sleep(SLEEP_MINUTES):
        # time.sleep() cannot wake up again, so use Java Thread.sleep() instead
        # time.sleep(SLEEP_MINUTES*60)
    if isJython():

        from java.lang import Thread
        Thread.sleep(SLEEP_MINUTES * 60 * 1000)
    else:
        import time
        time.sleep(SLEEP_MINUTES * 60)
