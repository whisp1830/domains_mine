# -*- coding: utf-8 -*-

"""
根据自定义相似度聚类,结合mongo同步进行
"""

from domain_match_rule import Domains_Match
from pymongo import MongoClient
from datetime import datetime
from config_file import mongo_ip,IS_TEST
from config_file import mongo_db_name_samples,mongo_db_name
from config_file import mongo_clusters_table
import database.mysql_operation


mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','idomains_mine_locate','utf8')
mongo_db_name = mongo_db_name_samples if IS_TEST else(mongo_db_name)
mongo_db = MongoClient(mongo_ip,27017)[mongo_db_name]

def cluster(domains):

    print "cluster begin..."
    clusters_table = mongo_db[mongo_clusters_table]
    dm_class = Domains_Match()
    if len(domains) != 0:
        if clusters_table.find({}, {}).count()==0:
            clusters_table.insert_one(
                {
                    'templet_domain': domains[0],
                    'update_time': datetime.now(),
                    'existed_similar_domains': [],
                    'modes': []
                }
            )
            domains = domains[1:]
        print domains
        for i,domain in enumerate(domains):
            match_flag = 0
            if not clusters_table.find_one({'existed_similar_domains':domain}, {}):
                print '{0}:{1}'.format(i + 1, domain)
                for rs in clusters_table.find({}, {'_id': 0, 'templet_domain': 1}):
                    match_domain = rs['templet_domain']
                    flag,mode = dm_class.match(match_domain,domain)
                    if flag:
                        match_flag = 1
                        clusters_table.update_one(
                            {'templet_domain': match_domain},
                            {
                                '$set': {
                                    'update_time': datetime.now()
                                },
                                '$addToSet': {
                                    'existed_similar_domains': domain,
                                    'modes': mode
                                }
                            },
                            upsert=True
                        )
                if match_flag == 0:
                    clusters_table.insert_one(
                        {
                            'templet_domain': domain,
                            'update_time': datetime.now(),
                            'existed_similar_domains': [domain],
                            'modes': []
                        }
                    )
    print "cluster end..."

def exper_cluster():
    import pickle
    from config_file import samples_file_name

    sql = "select domain from illegal_domains_index"
    domains = list(mysql_conn.exec_readsql(sql))
    for i in range(len(domains)):
        domains[i] = domains[i][0]
    print (domains)
    print len(domains)
    cluster(domains)

if __name__ == "__main__":
    exper_cluster()