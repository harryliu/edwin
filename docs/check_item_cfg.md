# check item的配置
edwin还没有的admin页面来提供check item的配置, 如果你有兴趣的话, 欢迎为edwin提供一个admin模块. 在没有admin模块之前, 我们不得不直接在DB中配置相应的表, 不用担心, 其实非常简单. 

## 1. team的设置 
表EDWIN_TEAM_CFG中, 可以配置team的基本信息. 字段清单见下: 

| 字段        | 含义   |  备注  |
| --------   |  :-----  | :----  |
| OWNER_TEAM_CODE| Team的编码 |       |
| EMAIL_TO_LIST| Team的邮箱列表     |若是多个邮箱号，以英文逗号或分号分隔  |
| SMS_MAIL_TO| Team的短信告警对应的邮箱号 |   |
| SMS_MAIL_TITLE| Team的短信告警对应的邮箱标题       |   |
| PHONE_MAIL_TO|  Team的电话告警对应的邮箱号    |   |
| PHONE_MAIL_TITLE|Team的电话告警对应的邮箱标题   |  |


## 2. check item的设置 
在表EDWIN_CHECK_ITM_CFG中配置检查项目. 字段清单见下:  

| 字段        | 含义   |  备注  |
| --------   |  :-----  | :----  |
|ITM_CODE|  check item的编码| 这是唯一键      |
|ITM_TITLE| check item的标题 | 这个将显示在web页面      |
|ITM_CATEGORY | check item的类别 |       |
|ENABLED_FLAG| 启用标志, Y为启用, N为禁用 |       |
|HOST| 检查agent部署在哪个机器上 | 仅仅是为了信息的完整性, edwin服务器并不会自动启动agent  |
|CHECK_SCRIPT| agent程序的详细路径 | 仅仅是为了信息的完整性, edwin服务器并不会自动启动agent      |
|CHECK_INTERVAL_MINUTE| agent程序的执行频率 | edwin服务器用这个值来判断你的agent是否超期未运行      |
|CHECK_VALUE_IS_NUMBER| 检查结果是否可以量化, Y为可量化, N为不可量化 |       |
|DESCRIPTION  | check item的说明 |       |
|OWNER_TEAM_LIST| 负责的team code  |如果是多个team共同负责, 以英文逗号或分号分隔team code       |
|WARNING_LIMIT| 警告级极限值 | 对于检查结果可量化的check item, 必须设定该值      |
|CRITICAL_LIMIT| 紧急级极限值 | 对于检查结果可量化的check item, 必须设定该值     |
|SHADOW_DATA| 影子 Data, 该值将和你的检查结果一起保存到EDWIN_CHECK_ITM_LOG表中 |很高端的属性哦, 后面细讲|
|WARNING_MAIL_CC| 警告级异常会抄送給谁 |       |
|CRITICAL_MAIL_CC| 紧急级异常会抄送給谁 |       |
|CRITICAL_SMS_FLAG| 对于紧急级异常, 是否允许发送短信告警 |       |
|CRITICAL_CALL_FLAG| 对于紧急级异常, 是否允许电话告警  |       |
|ALLOW_REPEATED_SMS_ALARM| 是否允许重复短信报警 |       |   
|ALLOW_REPEATED_CALL_ALARM| 是否允许重复电话报警 |       |  
|ALLOW_REPEATED_MAIL_ALARM | 是否允许重复邮件报警 |       |

**SHADOW_DATA** 的高级用法   

举例说明吧, 比如我们想要监控windows机器C盘和D盘的使用情况, 假定紧急级的条件分别是, C盘大于70%使用量, D盘80%的使用量. 我们有两种做法:  

1. 分别C盘和D盘配置不同的check item, 当然对应这需要两个agent程序. 很显然, 两个agent程序代码几乎一模一样, 写两个几乎一模一样的程序, 这并不是好的做法. 另外, 机器一多的话, 按照这样的做法, 我们的check item会暴增, 管理起来也很不便.  

2. 另一个推荐的做法是, 配置一个check item来支持两个盘的检查, 但由于两个盘的极限值不同, 如何编写这个agent呢? 很简单, 我们为SHADOW_DATA加入一些指令, 比如 "C_disk_critical=0.70 || C_disk_critical=0.80",  在agent程序中,我们通过api获取到这个指令, 并做解析, 得到C盘和D盘各自设定的极限值, 按照极限值检查实际的磁盘使用量即可. 

## 3. 展现页面的配置 
之前介绍过, edwin对于检查项的组织形式, 由小到大是: check item -> pagelet -> page -> dashboard, 其中page是edwin的一个具体展现页面, 一个展现页面包含多个 pagelet(即豆腐块), 一个豆腐块可以包含多个check item. 另外, edwin提供一个dashboard固定展现页, 自动汇总其他展现页的监控结果.  

edwin可以支持多个team, 为了方便各个team监控, 很自然地可以为不同的team配置不同的page页.  

在实际的实施中, 常会碰到这样一个现象, 同一个server可能好几个team共用, 对于这个server的监控, 这几个team可能都很关心.edwin 可以很轻松解决这种交叉关注问题. 因为, 在edwin中一个check item 可以出现在多个豆腐块(pagelet)下, 也就意味着, 一个check item可以出现在多个展现页中, 问题解决了, 就这么简单. 

### 3.1 page页的配置
表EDWIN_PAGE中, 可以配置page属性, 字段清单见下: 

| 字段        | 含义   |  备注  |
| --------   |  :-----  | :----  |
|PAGE_CODE | page页的编码| 主键     |
|PAGE_TITLE| page页在web上的显示名称|      |
|DISPLAY_FLAG|是否要在web上显示 | Y为显示, N为不显示     |
|DESCRIPTION|| 该page页的描述     |


### 3.2 豆腐块(pagelet)的配置 
表EDWIN_PAGELET中, 可以配置page属性, 字段清单见下: 

| 字段        | 含义   |  备注  |
| --------   |  :-----  | :----  |
|PAGELET_CODE|pagelet的编码| 主键     |
|PAGELET_TITLE|pagelet在web上的显示名称|      |
|PAGE_CODE|所属的page编码|      |
|DISPLAY_ORDER|在page上的显示次序| 序号越小越靠前显示     |
|DISPLAY_FLAG|是否要在page上显示|  Y为显示, N为不显示     |
|DESCRIPTION|该pagelet的描述|      |     


### 3.3 豆腐块(pagelet)下要显示哪些check item
在表EDWIN_PAGELET_CHECK_LIST, 可配置某个豆腐块要显示哪些check item中, 段清单见下:  
 
| 字段        | 含义   |  备注  |
| --------   |  :-----  | :----  |
|PAGELET_CODE| pagelet的编码|      |
|CHECK_ITM_CODE|包含了哪个check item|      |
|DISPLAY_ORDER| check item在pagelet中的显示次序| 序号越小越靠前显示     |
|DISPLAY_FLAG|是否要在pagelet上显示|  Y为显示, N为不显示        |



## 3. 检查结果表  
表EDWIN_CHECK_ITM_LOG中, 保存着详尽的检查结果, 字段清单见下:  

| 字段        | 含义   |  备注  |
| --------   |  :-----  | :----  |
|ITM_CODE| check item的编码|      |
|CHECK_DATE|检查日期|      |
|CHECK_TIMESTAMP| 检查的详细时间|   |
|CHECK_STATUS|检查的结果, 正常/警告级异常/紧急级异常|     |
|CHECK_VALUE|检查的具体数值| 仅适用于检查结果可量化的check item   |
|CHECK_DETAIL_MSG|检查结果的详尽描述, 用于web展现|支持html写法, 如果你要显示小于号, 需要做html转义|
|CHECK_NOTIFICATION_MSG|检查结果的详尽描述, 用于异常时的邮件通知|支持html写法, 如果你要显示小于号, 需要做html转义 |
|WARNING_LIMIT|警告级极限值| 仅适用于检查结果可量化的check item      |
|CRITICAL_LIMIT|紧急级极限值| 仅适用于检查结果可量化的check item      |
|SHADOW_DATA|影子 Data, 该值来源于check item配置表的SHADOW_DATA字段 |     |
|IS_WARNING_EVENT|是否是警告级异常, 取值Y或N|  |
|IS_CRITICAL_EVENT|是否是紧急级异常, 取值Y或N|     |
|IS_NEW_WARNING_EVENT|是否是新的警告级异常, 取值Y或N|     |
|IS_NEW_CRITICAL_EVENT|是否是新的紧急级异常, 取值Y或N|     |
|ALARM_SEND_STATUS|报警发送状态| 有异常才会报警    |
|ALARM_SEND_BEGIN_TIME|报警发送的开始时间|     |
|ALARM_SEND_END_TIME|报警发送的结束时间|     |

