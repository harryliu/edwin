##What is edwin
edwin is one alerting and monitoring system written in Python. 


##Why to invent edwin
Many monitoring softwares existed out there, such as Nagios, Ganglia, Zenoss.   
I just want to re-invent a new wheel to explore the Python language power. 
We can use edwin to monitor any metrics besides server status  


##edwin Components  
1. **edwinServer.Web**, served as web service and web GUI.  
   Deployed on server machine. It requires Python 2.7.  
2. **edwinServer.Scripts**, send alarm and do housekeeping tasks.  
   Deployed on server machine. It requires Python 2.7. 
3. **edwinAgent**, do check task, and register check result to server.   
   Deployed on client machines. It requires Jython 2.7. 


##How to work
Let us to break down several steps below,    
1. The script of edwinAgent check first, then send result to edwinServer.Web via web service.    
2. edwinServer.Scripts.send_alarm will send out alarm if the checking result is abnormal.    
3. In edwinServer.Web, the checking result can be showed in dash-board.   


##Features
1. Every check item has two kinds of abnormal limit, they are **warning** and **critical**.  
   For warning events, they will be sent via email.
   For critical events, they can be sent via SMS and calling if enabled.    
2. Edwin define the  you to customize alarm delivery options, includes,
   one option to allow repeated email alarm
   one option to allow repeated SMS alarm
   one option to allow repeated call alarm 
3. Basic statistics trend charts are available for every check item.






   
    




  