
## 简单介绍一下edwin
edwin是一个报警和监控平台, 可以使用它监控任意东西, 如有异常(分为警告级和严重级), 可以发出报警. 可以自定义报警的通知方式, 比如邮件/短信/电话. 另外, 它提供一个web UI, 能以dashboard形式展现监控指标的状态.  

edwin对于监控项目的组织形式, 由小到大是:  check item -> pagelet -> page -> dashboard.  另外,可以为 check item指定一个或多个 team 来负责. 这样灵活的组织形式, 使得edwin非常适合管理大量监控条目. 

一句话, **edwin 是一个非常适合团队使用的监控报警平台, 而且也适合多个团队共用. ** 


## edwin 组件  
1. **edwinServer.Web**, 做为web service和 web 展现页面.   
   需要部署在你的服务器上, 需要Python2.7, 具体见 requirements_Server.txt 文档
2. **edwinServer.Scripts**, 有脚本专门发送告警  
   部署在你的服务器上, 推荐和edwinServer.Web放在同一个机器上, 当然也可以不放在一起. 安装环境见 requirements_Server.txt 文档
3. **edwinAgent**, 你的检查脚本即是一个agent, edwin已经提供了agent开发示例   
   部署在你想要的机器上, 运行环境是jython2.7和python2.7, 考虑到jython安装非常方便, 推荐使用jython2.7



## edwin是如何工作的

###首先声明两个概念, 下面的文档 
1. 检查状态, 即你的check item是否正常, 在edwin中, 有三种检查状态:正常/警告级异常/严重异常
2. 检查结果, 分为两种: 即可以可量化的, 以及也不可量化的. 对于可量化的, 你的agent需要登记检查值, 对于不可量化的check item, 你的agent需要登记检查状态.   

###edwin工作方式非常简单, 一共三步:     
1. 在客户端机器上运行你的agent脚本, 即完成检查, 通过web service将检查结果保存在服务器端.      
2. *dwinServer.Scripts.send_alarm* 组件定时查看检查结果, 如有异常会发出报警.  
3. *edwinServer.Web* 会在web页面上以醒目的方式展现检查结果. 



## guide 说明
1. 对于可量化的check item, 你需要在数据库中设置警告级临界值和严重级临界值. 你的agent只需要登记实际检查值即可, 服务器端自动判断报警级别. 
2. 对于不可量化的check item, 你的agent程序需要给出检查状态, 即正常抑或警告或紧急. 
3. 告警发送方式   
   *对于警告级异常, edwin会以email方式发出警告  
   *对于紧急级异常, edwin会以邮件/短信/电话的方式发出警告, 当然可以禁掉短信/电话的告警方式  
4. 重复警告的处理
谁都不想收到一堆重复的警告, 尤其是不那么重要或者检查频率高的check item, edwin为每个check item提供三个开关来控制是否允许重复告警, 分别是ALLOW_REPEATED_MAIL_ALARM、ALLOW_REPEATED_SMS_ALARM和ALLOW_REPEATED_CALL_ALARM
5. Web提供为每个check item提供基本的趋势图， 帮助我们回顾检查的结果
