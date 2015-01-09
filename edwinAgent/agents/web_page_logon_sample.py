# -*- coding: utf-8 -*-
'''
test the landing page response
'''
from __future__ import absolute_import
import logging
import logging.config
from edwinAgent.common import const
from edwinAgent.common import conf  
from edwinAgent.common import api_helper
from edwinAgent.common import os_helper
from edwinAgent.common import my_logging
import datetime


 
#logging.basicConfig(level=logging.DEBUG)      # use for development
log_file=os_helper.getLoggingFileName(__file__)
root_logger=logging.getLogger() 
my_logging.configureLogger(root_logger, log_file, conf.log_level)
logger=logging.getLogger(__name__)  # get current file logger



 

def check():
    '''
    get check result, the result format is (check_value, detail_msg)
    '''    
    import urllib, urllib2, cookielib 
    cj = cookielib.CookieJar() 
    tim1=datetime.datetime.now()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    # prepare form elements 
    login_data = urllib.urlencode({'employeeNo' : 'your_name', 'password' : 'your_pwd'}) 
    login_url='http://10.1.2.3/your_site/userlogin'
    #post the login form
    f=opener.open(login_url, login_data) 
    responseStr = f.read() 
    if responseStr.find('Your username or password is wrong!')>=0:
        f.close()
        opener.close()
        raise Exception('your_site system, Your username or password is wrong!')
    else:
        #to visit the landing page
        #tim1=datetime.datetime.now()
        operation_url='http://10.1.2.3/your_site/reports/report.do?method=getTableData'
     
        f=opener.open(operation_url) 
        responseStr = f.read() 
        tim2=datetime.datetime.now()
        f.close()
        opener.close()
        check_value=(tim2-tim1).total_seconds()
        detail_msg="Get response time."
        return (check_value,detail_msg)




def main(itm_code):
    try:
        try:
            (check_value,detail_msg)=check()
        except Exception , e:
            logger.exception(e)
            exception_msg="%s"%e
            api_helper.registerException(itm_code,exception_msg)      
        else:
            logger.info("Check value: %d"%check_value)
            logger.info("Check detail message: %s"%detail_msg)
            (successful, echo_msg)=api_helper.updateNumericalResult(itm_code, check_value, detail_msg)        
            if successful:
                logger.info("update status successful.")
            else:
                logger.info("fail to update status. echo message: %s"%(echo_msg,))
                  
    except Exception, e:
        logger.exception(e)


if __name__=="__main__":
    itm_code='WEB_PAGE_LOGON_SAMPLE'
    logger.info("=================================")
    logger.info("===check item: %s"%itm_code)
    logger.info("=================================")
    
    main(itm_code)
    
    logger.info("===End to check: %s"%itm_code)

