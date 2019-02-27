# -*- coding: utf-8 -*-

"""
根据匹配模式生成域名,并验证域名的存在性
        -:删除指示符
        &:连续指示符
        
        #:数字通配符
        *:字母通配符
        $:数字/字母通配符
        %:顶级域通配符
"""
from database import mysql_operation
from copy import copy
import dns.resolver
import pickle
from pymongo import MongoClient
from datetime import datetime
from gevent_model import run_gevent
from divide_items import divide_items
from config_file import dns_server_file_name,IS_TEST
from config_file import tld_list_fn
from config_file import mongo_ip,mongo_db_name,mongo_db_name_samples
from config_file import mongo_similar_domains_table

with open(tld_list_fn,'rb') as f:
    tld_list = pickle.load(f)

mongo_db_name = mongo_db_name_samples if IS_TEST else(mongo_db_name)
mongo_db = MongoClient(mongo_ip,27017)[mongo_db_name]
MysqlConn = mysql_operation.MysqlConn('10.245.146.37','root','platform','idomains_mine_locate','utf8')
class GenerateVaildDomain():

    def __init__(self,threads_num):

        with open(dns_server_file_name) as f:
            self.dns_resolvers = [dns_resolver.strip() for dns_resolver in f.readlines()]
        self.name_server_num = len(self.dns_resolvers)
        self.general_list = 'abcdefghijklmnopqrstuvwxyz0123456789'
        self.alpha_list = 'abcdefghijklmnopqrstuvwxyz'
        self.digit_list = '0123456789'
        self._threads_num = threads_num
        self.resolvers = [dns.resolver.Resolver(configure=False) for _ in range(self._threads_num)]
        for i, resolver in enumerate(self.resolvers):
            resolver.lifetime = resolver.timeout = 12.0
        self.scan_count = 0
        self.valid_count = 0

    def set_queue(self):

        self.domain_queue = []
        self.ips_queue = []
        self.existed_domains = set()

    def validate_domain(self,domain, j):
        """
        验证域名是否存在
        :param domain: 
        :param j: 
        :return: 
        """
        ips_list = []
        try:
            answers = self.resolvers[j].query(domain)
        except dns.resolver.NoAnswer, e:
            pass
        except dns.resolver.NXDOMAIN, e:
            pass
        except dns.resolver.NoNameservers, e:
            pass
        except Exception,e:
            pass
        else:
            ips = [answer.address for answer in answers]
            if '1.1.1.1' not in ips and '127.0.0.1' not in ips and '0.0.0.0' not in ips:
                ips_list = ips
                self.domain_queue.append(domain)
                self.ips_queue.append(ips)

        return ips_list

    def validate_domains(self,j,domains):

        self.resolvers[j].nameservers = [self.dns_resolvers[j% self.name_server_num]]
        for domain in domains[j]:
            self.validate_domain(domain,j)

    def generate_by_delete(self,templet_domain, exists_domains):
        """
        通过删除一个字符来产生域名
        :param templet_domain: 
        :param exists_domains: 
        :return: 
        """
        domains = set()
        for i in range(len(templet_domain)):
            if i == 0:
                domain = ''.join(list(templet_domain)[1:])
            else:
                domain = ''.join(list(templet_domain)[:i]
                                 + list(templet_domain)[i + 1:])
            if domain not in exists_domains:
                domains.add(domain)
            else:
                self.existed_domains.add(domain)

        return domains

    def generate_domains(self,mode, exists_domains):
        """
        产生有效域名集合
        :param mode: 枚举模式
        :param exists_domains: 该模式下已获取的域名
        :return: 该模式下所有有效域名
        """
        self.set_queue()
        add_domains = set()
        # if mode[-1] == '-':
        #     mode = mode.replace('-', '')
        #     add_domains = self.generate_by_delete(mode, exists_domains)
        if mode.find('%')!=-1:
            for tld in tld_list:
                str1 = mode
                add_domains.add(str1.replace('%',tld))
        else:
            if mode.find('&') != -1:
                mode = mode.replace('&', '')
                is_continuous = 1
            else:
                is_continuous = 0

            modes = []
            modes.append(mode)
            while len(modes) != 0:
                item = modes.pop(0)
                if item.find('#') != -1:
                    wildcard = '#'
                    enumeration = copy(self.digit_list)
                elif item.find('*') != -1:
                    wildcard = '*'
                    enumeration = copy(self.alpha_list)
                elif item.find('$') != -1:
                    wildcard = '$'
                    enumeration = copy(self.general_list)
                else:
                    if item not in exists_domains:
                        add_domains.add(item)
                    else:
                        self.existed_domains.add(item)
                    continue

                for ch in enumeration:
                    str1 = item
                    mode = str1.replace(wildcard, ch) if is_continuous else(str1.replace(wildcard, ch, 1))
                    modes.append(mode)

        items,part_num = divide_items(list(add_domains),self._threads_num)
        self.scan_count += len(add_domains)
        run_gevent(self.validate_domains,items,threads_num=part_num)
        add_domains = self.domain_queue
        add_ips = self.ips_queue
        existed_domains = list(self.existed_domains)
        self.valid_count += len(add_domains)
        print '{0}:{1}'.format('scan_count',self.scan_count)
        print '{0}:{1}'.format('valid_count', self.valid_count)

        return add_domains,existed_domains,add_ips

def exper(mode):
    """
    '##&001524.com'
    '00##&1524.com'
    :return: 
    """
    import datetime
    t1 = datetime.datetime.now()
    gvd = GenerateVaildDomain(10)
    add_domains, existed_domains,add_ips = gvd.generate_domains(mode,[])
    # add_domains, add_ips = gvd.generate_domains('00038*.com', ['00038x.com', '00038a.com'])
    for add_domain,add_ip in zip(add_domains,add_ips):
        print add_domain,add_ip
    for existed_domain in existed_domains:
        print existed_domain
    t2 = datetime.datetime.now()
    print t2-t1

def load_cur_modes(config_modes=True):
    add_modes, existed_domains_list = [],[]
    mongo_clusters_table = "clusters"
    clusters_table = mongo_db[mongo_clusters_table]
    #print clusters_table.find({},{}).count()
    fetch_data = clusters_table.find({},{'existed_similar_domains':1,'modes':1})
    for item in fetch_data:
        add_modes.append(item['modes'])
        existed_domains_list.append(item['existed_similar_domains'])
    return add_modes,existed_domains_list
    #add_modes, existed_domains_list = clusters_table

    

def generate_similar_domains(config_modes=True,threads_num=20):
    MysqlConn = mysql_operation.MysqlConn('10.245.146.37','root','platform','idomains_mine_locate','utf8')
    similar_domains_table = mongo_db[mongo_similar_domains_table]
    gvd = GenerateVaildDomain(threads_num)
    add_modes, existed_domains_list = load_cur_modes(config_modes=config_modes)#load_cur_modes导出域名的生成模式和已存在域名列表#
    counter = 0
    for i,rs in enumerate(zip(add_modes,existed_domains_list)):
        #print i,rs
        mode,existed_domains = rs
        print '{0}:{1}'.format(i+1,mode)
        if mode :
            add_domains, existed_domains, add_ips = gvd.generate_domains(mode[0],existed_domains)
            for i in range(len(add_domains)):
                    sql = "INSERT INTO possible_illegal_domains_index(domain,source) VALUES('%s','%s')\
                        ON DUPLICATE KEY UPDATE domain='%s',source='%s';"%(add_domains[i],'similar_domains_method',add_domains[i],'similar_domains_method')
                    res = MysqlConn.exec_cudsql(sql)
                    if  res:
                        counter += 1
                        print counter
        if counter >100:
            MysqlConn.commit()
            counter = 0
            similar_domains_table.update_one(
            {'mode':mode},
                    {
                        '$set':{
                        'mode':mode,
                        'insert_time':datetime.now()
                    },
                    '$addToSet':{
                        'add_domains':{'$each':add_domains},
                        'existed_domains': {'$each': existed_domains},
                        'add_ips': {'$each': add_ips},
                    }
            },
            upsert=True
                )
    MysqlConn.commit()

    MysqlConn.close_db()
if __name__ == "__main__":
    generate_similar_domains()
    #exper('4107###&.com')