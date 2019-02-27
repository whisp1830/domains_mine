#-*-coding: utf8 -*-

"""
同a/ip记录反查域名
"""
import sys
sys.setrecursionlimit(10000)
from datetime import datetime
from bs4 import BeautifulSoup
from driverhandler import DriverHandler
from tldextract import extract
import urllib2
import time
import sys
import Queue
import threading
import database.mysql_operation

mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','idomains_mine_locate','utf8')
ip_to_get = Queue.Queue()



class BGPSpider(DriverHandler):
    """
    https://bgp.he.net/ip/43.229.6.43#_dns
    """

    def __init__(self, timeout=60):

        DriverHandler.__init__(self,'chrome',max_time=timeout)
        self.result = {}
        self.counter=0
        self.base_url = 'https://bgp.he.net/ip/{ip}#_dns'

    def spider(self, ip):

        self.counter+=1
        if not self.result.get(ip):
            self.result[ip] = {}
            self.result[ip]['cur_time'] = datetime.now()
        url=self.base_url.format(ip=ip)
        domains=set()
        flag=self.open_web(url)
        if flag:
            try:
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
            except Exception, e:
                print "parse error:",str(e)
            else:
                div_tip = soup.find(name='div', attrs={'id': 'dns'})
                if div_tip:
                    a_tips = div_tip.find_all(name='a', title=True)
                    for a_tip in a_tips:
                        domain = a_tip.attrs['title'].strip()
                        domains.add(domain)
        if not flag or self.counter%10==0:
            self.destory_driver()
            self.create_driver()
            self.counter=0
        self.result[ip]['domains']=domains
        result=dict(ip=ip,**self.result[ip])
        del self.result[ip]

        return result

class DomainBigDataSpider(object):
    """
    https://domainbigdata.com/
    """

    def __init__(self, timeout=10,wait_time=1):

        self.result = {}
        self.base_url = 'https://domainbigdata.com/{ip}'
        self.timeout = timeout
        self.wait_time=wait_time

    def spider(self, ip):
        """

        :param ip: 
        :return: 
        """
        domains=set()
        if not self.result.has_key(ip):
            self.result[ip] = {}
            self.result[ip]['cur_time']=datetime.now()
        try:
            response = urllib2.urlopen(self.base_url.format(ip=ip), timeout=self.timeout)
            time.sleep(self.wait_time)
        except Exception, e:
            print "get error:",str(e)
        else:
            try:
                soup = BeautifulSoup(response, 'lxml')
            except Exception,e:
                print "parse error:",str(e)
            else:
                lis = soup.find(name='div', attrs={'id': 'MainMaster_divRptDomainsOnSameIP'})
                if lis:
                    a_tips = lis.find_all(name='a', href=True)
                    domains = domains|set([a_tip.text.strip() for a_tip in a_tips])
        self.result[ip]['domains']=domains
        result = dict(ip=ip, **self.result[ip])
        del self.result[ip]

        return result


class AizhanSpider(object):
    """
    dns.aizhan.com　
    """

    def __init__(self, timeout=5, wait_time=2):

        self.base_url = "https://dns.aizhan.com/%s/%d/"  # 基址
        self.timeout = timeout
        self.wait_time = wait_time

    def spider(self, ip, page_index=0):
        """
        获取页面源
        :param ip: 
        :param page_index: 
        :return: 
        """
        if page_index<0:
            print "page index is error!"
            sys.exit(-1)
        print "spider the %dth page"%(page_index+1)
        if page_index == 0:
            self.page_num = -1
            self.result = {}
        if not self.result.has_key(ip):
            self.result[ip] = {}
            self.result[ip]['cur_time']=datetime.now()
            self.result[ip]['domains']=set()
        if page_index==0 or page_index < self.page_num:
            url = self.base_url % (ip, page_index)
            try:
                response = urllib2.urlopen(url, timeout=self.timeout)
                time.sleep(self.wait_time)  # 等待数据加载
            except Exception, e:
                print "get error:",str(e)
            else:
                try:
                    soup = BeautifulSoup(response, 'lxml')
                except Exception, e:
                    print "parse error:", str(e)
                else:
                    if page_index == 0:
                        ul_tip=soup.find(name='div',attrs={'class':'dns-infos'}).ul
                        if ul_tip:
                            lis=ul_tip.find_all(name='li')
                            if len(lis)==3:
                                domains_num=int(lis[2].span.text.strip())
                                self.page_num=domains_num//20
                                if domains_num%20!=0:self.page_num+=1
                                if self.page_num>5:
                                    self.page_num = 5;
                                print "has %d pages"%self.page_num
                    domains_tip=soup.find_all(name='td',attrs={'class':'domain'})[1:]
                    for domain_tip in domains_tip:
                        domain=domain_tip.a.text.strip()
                        domain=extract(domain).registered_domain
                        if domain:
                            self.result[ip]['domains'].add(domain)
            self.spider(ip,page_index=page_index+1)

        result = self.result[ip]

        return dict(ip=ip,**result)

def exper(ip,spider_id=1):

    if spider_id==1:
        bgp=BGPSpider()
        #print bgp.spider(ip)
        bgp.destory_driver()
        return bgp.spider(ip)
    elif spider_id==2:
        dbd=DomainBigDataSpider()
        print dbd.spider(ip)
        return dbd.spider(ip)
    else:
        aizhan=AizhanSpider()
        print aizhan.spider(ip)
        return aizhan.spider(ip)

def get_ip_queue():
    res = list(mysql_conn.exec_readsql("SELECT ip from illegal_ip_index;"))
    for _ in res:
        ip_to_get.put(_[0])
    print ip_to_get.qsize()
    pass

def find_reverse():

    counter = 0
    ip_to_get = list(mysql_conn.exec_readsql("SELECT ip from illegal_ip_index;"))
    for ip in ip_to_get:
        ip = ip[0]
        domains = list(exper(ip,spider_id=3)['domains'] | exper(ip, spider_id=2)['domains'] | exper(ip,spider_id=3)['domains'])
        for domain in domains:
            res = mysql_conn.exec_cudsql("INSERT INTO ip_reverse(ip,domain) VALUES ('%s','%s');"%(ip,domain))
            if res :
                 counter += 1
                 print counter
        if counter > 10:
            mysql_conn.commit()
            counter = 0
        print ip," detect finish"

    sql = "DELETE FROM ip_reverse where domain in (SELECT domain from possible_illegal_domains_index);INSERT INTO possible_illegal_domains_index(domain,source) SELECT distinct domain,'ip_reverse_method' FROM ip_reverse"
    mysql_conn.exec_cudsql(sql)
    mysql_conn.commit()

    mysql_conn.close_db()

def find_single_reverse(ip):
    counter = 0
    while ip_to_get.qsize>0:
        ip = ip_to_get.get()
        domains = list(exper(ip,spider_id=3)['domains'] | exper(ip, spider_id=2)['domains'] | exper(ip,spider_id=3)['domains'])
        for domain in domains:
            res = mysql_conn.exec_cudsql("INSERT INTO possible_illegal_domains_index(domain,source) VALUES ('%s','%s');"\
                                            "ON DUPLICATE KEY UPDATE domain='%s',source='%s';"%(domain,'ip_reverse_method',domain,'ip_reverse_method'))
            if res :
                 counter += 1
                 print counter
        if counter > 10:
            mysql_conn.commit()
            counter = 0
        print ip," detect finish"



def main():
    thread_num = 3
    get_ip_queue()
    thread_list = list();
    # 先创建线程对象
    for i in range(0, thread_num):
        thread_name = "thread_%s" %i
        thread_list.append(threading.Thread(target = find_single_reverse, name = thread_name, args = (20,)))
 
    # 启动所有线程
    for thread in thread_list:
        thread.start()
 
    # 主线程中等待所有子线程退出
    for thread in thread_list:
        thread.join()

    mysql_conn.commit()

    mysql_conn.close_db()



if __name__ == "__main__":
    main()
    #exper('43.229.6.43', spider_id=1)
    #print exper('43.229.6.43', spider_id=2)['domains']
    #print exper('43.229.6.43',spider_id=3)['domains']
    #for i in exper('43.229.6.43',spider_id=3)['domains'] | exper('43.229.6.43', spider_id=2)['domains'] | exper('43.229.6.43',spider_id=3)['domains']: