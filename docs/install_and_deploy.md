##Server side setup

###Database setup  
1. create tables, the SQL file is db_setup/DDL/oracle.sql. 
   It is easy to adopt for other RDBMS.   
2. initialize data in database, run all SQL files in db_setup/data

###edwinServer software setup
1. install Python 2.7 and Python packages listed in requirements_Server.txt
2. copy edwinServer folder to your server.  
3. configurations:
   edwinServer/common/conf.py: change db and email configurations    
   edwinServer/web/conf.py: change web server configurations 
   
    
##Configure your own check items  
 After database setup, you can find some sample data in the following database tables. You can configure your own refer to the sample data.  
  **EDWIN_TEAM_CFG**: team mailbox and SMS/call settings 
  **EDWIN_CHECK_ITM_CFG**: check item configuration
  **EDWIN_PAGE**: Edwin web can contains one dashboard and many pages, one EDWIN_PAGE record will have one web page   
  **EDWIN_PAGELET**: relationship of page and pagelet is 1:n 
  **EDWIN_PAGELET_CHECK_LIST**: relationship of pagelet and check item is 1:n
       
   
##Launch server side 
1. launch alarm service: execute edwinServer/bin/alarm_send.bat or alarm_send.sh
2. launch web server: execute edwinServer/bin/runserver.bat or runserver.sh


   
##Agent side setup
1. install Jython 2.7
2. copy edwinAgent folder to your computer.
3. configurations: 
   edwinAgent/common/conf.py: change web server url   
    
    
##Launch your agent
1. execute edwinAgent/bin/your_agent.sh or your_agent.bat 

