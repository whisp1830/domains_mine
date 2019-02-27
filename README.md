指定地区非法域名获取程序

****

获取方法：     

获取方法包含了IP反查、WHOIS注册信息反查、生成相似域名三种

获取流程：

1. 输入指定地区region，从数据库中选取IP地理位置在此地的数据

1. 将数据库中的非法域名、IP导入到possible\_illegal\_domains\_index中，准备进行之后的反查和检测，将数据来源标记为source\_domain

1. 根据基表中的IP反查域名，检测反查的域名是否为非法，非法则导入illegal\_domains\_index中，数据来源标记为ip\_reverse\_method

1. 根据illegal\_domains\_index中已被检测出非法的域名，将其进行聚类相似聚类，根据产生的模型生成域名并验证其存在性。若生成的域名存在则放入possible\_illegal\_domains\_index等待检测。检测后非法的域名导入illegal\_domains\_index中，数据来源标记为similar\_domains\_method

1. 先获取illegal\_domains\_index中每个域名的IP。若IP的地理位置在region。则将确定非法并位于REGION当地的域名、IP、非法类型导出至region\_without\_whois.csv

1. 利用WHOIS注册信息反查域名，检测反查的域名是否为非法，非法则导入illegal\_domains\_index中

1. 最后获取illegal\_domains\_index中每个域名的IP。若IP的地理位置在region。则将确定非法并位于REGION当地的域名、IP、非法类型导出至region\_have\_whois.csv

1. 最后导出的格式为 （域名，IP，非法类型）的CSV文件，分为包含WHOIS信息反查和不包含WHOIS信息反查两份（目前WHOIS去除无效信息方面，还有一定问题）
