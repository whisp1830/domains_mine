# encoding:utf-8

from IPReverse import ip_reverse
import SDM.similar_domain_cluster as cluster
import SDM.generate_valid_domain as generate_valid_domain
import whois_reverse.anadomain as whois_reverse
import socket
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import os

#数据库相关
import database.mysql_operation

#获取IP地理位置
import ip2region.ip2Region
import ip2region.exec_ip2reg
searcher = ip2region.ip2Region.Ip2Region("ip2region/ip2region.db")






def import_base_table(city):

	'''
		将该地区的非法域名和IP映射导入posssible_illegal_domains_index，
		所有非法IP导入illegal_ip_index
	'''

	import pymongo
	conn = pymongo.MongoClient('0.0.0.0',27017)
	db = conn['idomains_mine']

	new_collection = db['clusters']
	new_collection.drop()
	db.create_collection(name='clusters')
	new_collection = db['similar_domains']
	new_collection.drop()
	db.create_collection(name='similar_domains')

	mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','idomains_mine_locate','utf8')

	fetch = mysql_conn.exec_readsql("show tables")

	for _ in fetch:
		mysql_conn.exec_cudsql("DELETE FROM "+str(_[0]))

	sql_1 = "insert into possible_illegal_domains_index(domain,source) select distinct domain,'source_data'"\
			" from illegal_domains_profile_analysis.domain_ip_relationship where ip_city='%s';"%(city+'市')

	print sql_1
	mysql_conn.exec_cudsql(sql_1)
	mysql_conn.commit()
	#导入域名

	sql_2 = " insert into illegal_ip_index(ip) select ip from illegal_domains_profile_analysis.ip_general_list"\
			" where city='%s' union select ip from illegal_domains_profile_analysis.domain_ip_relationship"\
			" where ip_city='%s';"%(city+'市',city+'市')

	print sql_2
	mysql_conn.exec_cudsql(sql_2)
	mysql_conn.commit()
	#导入IP

	mysql_conn.close_db()


def import_illegal_table(source):

	'''
		将可疑域名中已被检测为非法的域名导入illegal_domains_index
	'''
	mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','idomains_mine_locate','utf8')

	sql = " insert into illegal_domains_index(domain,illegal_type,result_flag,source)"\
		  " select domain,illegal_type,result_flag,source from possible_illegal_domains_index"\
		  " where illegal_type not in ('未知','安全','') and source='%s'"%(source)
	mysql_conn.exec_cudsql(sql)
	mysql_conn.commit()
	mysql_conn.close_db()


def getIp(domain):
	myaddr = socket.getaddrinfo(domain,'http')[0][4][0]
	return myaddr

def get_ip_location(ip):
	return ip2region.exec_ip2reg.get_ip_geoinfo(searcher,ip)


def check_ip_region(region,have_whois=False):
	'''
		根据所有illegal_domains_index中的域名，
		先获取每个域名的IP，
		后解析该域名的IP地理位置，
		若该域名IP在传入的参数region地区内,
		则将域名导出至最后结果
	'''
	mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','idomains_mine_locate','utf8')
	sql = "select domain from illegal_domains_index where ip is null"
	res = mysql_conn.exec_readsql(sql)
	for _ in res:
		try:
			ip = getIp(_[0])
			print get_ip_location(ip)
			print _[0],ip
			mysql_conn.exec_cudsql("UPDATE illegal_domains_index SET ip='%s',province='%s',city='%s'"\
								   "WHERE domain='%s';"%(ip,get_ip_location(ip)['region'],get_ip_location(ip)['city'],_[0]))
		except:
			pass
	mysql_conn.commit()

	res = mysql_conn.exec_readsql("select domain,ip,illegal_type from illegal_domains_index where city='%s'"%(region+'市'))
	with open("region_%s.csv"%('has_whois' if have_whois else 'without_whois'),"w") as f:
		f.writelines('DOMAIN,IP,ILLEAL_TYPE\n')
		for _ in res:
			print _
			f.writelines(_[0]+','+_[1]+','+_[2]+'\n')

	mysql_conn.close_db()





if __name__ == "__main__":
	
	#将域名和IP导入基表
	region = '北京市'
	if '\xe5\xb8\x82' in region:
		region = region[0:6]	#若输入地域中含有“市”,将该汉字去掉
	print region
	import_base_table(region)
	


	#根据基表中的IP反查域名，检测反查的域名是否为非法，非法则导入illegal_domains_index中
	ip_reverse.find_reverse()
	os.system(" python detect/sample_detect.py")
	import_illegal_table('source_data')
	import_illegal_table('ip_reverse_method')
	

	#导入相似域名，并检测其中非法的域名导入illegal_domains_index
	cluster.exper_cluster()
	generate_valid_domain.generate_similar_domains()
	os.system(" python detect/sample_detect.py")
	import_illegal_table('similar_domain_method')

	check_ip_region(region)


	#利用WHOIS注册信息反查域名，检测反查的域名是否为非法，非法则导入illegal_domains_index中
	whois_reverse.run()
	os.system(" python detect/sample_detect.py")
	import_illegal_table('name_reverse')
	import_illegal_table('email_reverse')
	import_illegal_table('phone_reverse')


	check_ip_region(region,have_whois=True)








