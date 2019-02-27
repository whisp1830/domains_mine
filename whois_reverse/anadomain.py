# !encoding:utf-8

import MySQLdb
import re
import time
import tldextract

class initwhois():

    def __init__(self):
        print "Get whois from wjx begin!!!"

        self.host = '0.0.0.0'
        self.port = 3306
        self.user = 'root'
        self.passwd = ' '
        self.charset = 'utf8'
        self.database = 'idomains_mine_locate'

        self.table0 = 'illegal_domains_index'
        self.table1 = 'idomains_whois'
        self.target_table = 'source_domain_whois'

    def getwhois(self):

        #---------------------------
        print 'Begin connect!'
        conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, charset=self.charset, port=self.port)
        cursor = conn.cursor()
        conn.autocommit(1)
        print 'connect to ' + self.host
        #---------------------------

        sql_base = "insert into %s(domain,reg_name,reg_phone,reg_email) select domain,reg_name,reg_phone,reg_email "\
                    "from illegal_domains_profile.domain_whois_lite where domain in (select domain from %s)"\
                    " and reg_name is not null and reg_phone is not null and reg_email is not null"%(self.table1,self.table0)

        cursor.execute(sql_base)

        sql_find = "select domain, reg_name, reg_phone, reg_email from "+self.table1+" where domain in (select domain from "+self.table0+")"

        cursor.execute(sql_find)

        rows = cursor.fetchall()

        for row in rows:
            print row[0],row[1],row[2],row[3]
            SQL_Insert = 'replace into ' + self.target_table + ' (domain,reg_name,reg_phone,reg_email,flag) values(\'%s\',\'%s\',\'%s\',\'%s\',1)' % (row[0], row[1], row[2], row[3])
            print SQL_Insert
            cursor.execute(SQL_Insert)
            print "insert ok!!!"
        conn.close()
        cursor.close()


class Fakedomain():

    def __init__(self):
        print "Init Begin!"

        self.host1 = '0.0.0.0'
        self.port1 = 36666
        self.user1 = 'root'
        self.passwd1 = ' '
        self.charset1 = 'utf8'
        self.database1 = 'Beijing_WHOWAS'

        self.host2 = '0.0.0.0'
        self.port2 = 3306
        self.user2 = 'root'
        self.passwd2 = ' '
        self.charset2 = 'utf8'
        self.database2 = 'idomains_mine_locate'

        self.base1_table = 'domain_'
        self.base2_table = 'WHOIS_'
        self.filename = 'domain.txt'

        self.domain_table = 'source_domain_whois'


    @staticmethod
    def get_table_num(domain):
        """获取域名所属分表序号"""
        table_num = -1
        # 抽取首字母
        domain = str(domain).lower()
        try:
            initial = domain[0]
        except:
            table_num = -1
            return table_num
        # 基于 http://172.29.152.152:8000/dns_domain/beijing_whowas/Database/blob/master/bjwazwa.md 的
        # 数据库设计分表原则进行分表
        if domain.find("xn--") != -1 and initial == "x":
            table_num = 7
        elif initial == "s" or initial == "q" or initial == "x":
            table_num = 1
        elif initial == "c" or initial == "v":
            table_num = 2
        elif initial == "m" or initial == "n":
            table_num = 3
        elif initial == "a" or initial == "i":
            table_num = 4
        elif initial == "t" or initial == "h":
            table_num = 5
        elif initial == "b" or initial == "j" or initial == "o":
            table_num = 6
        elif initial == "p" or initial == "g":
            table_num = 7
        elif initial == "d" or initial == "l":
            table_num = 8
        elif initial == "f" or initial == "w" or initial == "u" or initial == "y" or initial == "z":
            table_num = 9
        elif initial == "e" or initial == "r" or initial == "k":
            table_num = 10
        else:  # 数字
            table_num = 8
        return table_num


    def yield_domain(self):
        file = open(self.filename, 'r')
        for line in file:
            yield line
        file.close()


    @staticmethod
    def reg_domain(domain):
        process = tldextract.extract(domain)
        return process.registered_domain

    def main(self):

        #---------------------------
        print 'Begin connect!'

        conn1 = MySQLdb.connect(host=self.host1, user=self.user1, passwd=self.passwd1, db=self.database1, charset=self.charset1, port=self.port1)
        cursor1 = conn1.cursor()
        conn2 = MySQLdb.connect(host=self.host2, user=self.user2, passwd=self.passwd2, db=self.database2, charset=self.charset2, port=self.port2)
        cursor2 = conn2.cursor()
        conn2.autocommit(1)

        print 'connect to ' + self.host1 + " and " + self.host2
        #---------------------------

        try:
            cursor2.execute("select domain from illegal_domains_index;")
            fetch_domains = cursor2.fetchone()
            for Domain in fetch_domains:
                Domain = Domain[0]
                #time.sleep(2)
                SQL_Find = 'select domain,reg_name,reg_phone,reg_email from WHOIS_' + str(Fakedomain.get_table_num(Domain)) + ' where domain=' + '\'' + Domain + '\''
                #print SQL_Find
                cursor1.execute(SQL_Find)
                row = cursor1.fetchone()
                #print row
                if row == None:
                    print 'Error', Domain
                else:
                    SQL_Insert = 'replace into ' + self.domain_table + ' (domain,reg_name,reg_phone,reg_email,flag) values(\'%s\',\'%s\',\'%s\',\'%s\',0)'%(row[0], row[1], row[2], row[3])
                    print SQL_Insert
                    cursor2.execute(SQL_Insert)
                    print 'Success', domain

            print 'Get domain whois OK!!'
        except:
            print "该地区没有符合要求的非法域名"

        
        conn1.close()
        conn2.close()
        cursor1.close()
        cursor2.close()

#-------------------------------------------------------------------------------------------------------------------------


class AnalysisData():

    def __init__(self):

        print "Init Begin!"

        self.host = '0.0.0.0'
        self.port = 3306
        self.user = 'root'
        self.passwd = ' '
        self.charset = 'utf8'
        self.database = 'idomains_mine_locate'

        self.domain_table = 'source_domain_whois'

        self.base_table = 'malicious_'
        self.name_table = 'malicious_name'
        self.phone_table = 'malicious_phone'
        self.email_table = 'malicious_email'

        self.group = ['name', 'phone', 'email']


    def main(self):

        #---------------------------
        print 'Begin connect!'
        conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, charset=self.charset, port=self.port)
        cursor = conn.cursor()
        conn.autocommit(1)
        print 'connect to ' + self.host
        #---------------------------

        for keyword in self.group:
            SQL_Select='select reg_' + keyword + ',count(*) from source_domain_whois group by reg_' + keyword
            cursor.execute(SQL_Select)
            rows = cursor.fetchall()
            for row in rows:
                print row, type(row)
                SQL_Insert='replace into ' + self.base_table + keyword + ' (reg_' + keyword + ',source_num) values(\'%s\',%s)'%(row[0], row[1])
                print SQL_Insert
                cursor.execute(SQL_Insert)
            print keyword, " is OK!"

        conn.close()
        cursor.close()


class searchback():

    def __init__(self):
        print "Init Begin!"

        self.host1 = '0.0.0.0'
        self.port1 = 36666
        self.user1 = 'root'
        self.passwd1 = ' '
        self.charset1 = 'utf8'
        self.database1 = 'Beijing_WHOWAS'

        self.host2 = '0.0.0.0'
        self.port2 = 3306
        self.user2 = 'root'
        self.passwd2 = ' '
        self.charset2 = 'utf8'
        self.database2 = 'idomains_mine_locate'

        self.base1_table = 'WHOIS_'
        self.base2_table = 'malicious_'
        self.new_table = 'whois_reverse_total'
        self.group = ['name', 'phone', 'email']


    def main(self):

        #---------------------------
        print 'Begin connect!'

        conn1 = MySQLdb.connect(host=self.host1, user=self.user1, passwd=self.passwd1, db=self.database1, charset=self.charset1, port=self.port1)
        cursor1 = conn1.cursor()
        conn2 = MySQLdb.connect(host=self.host2, user=self.user2, passwd=self.passwd2, db=self.database2, charset=self.charset2, port=self.port2)
        cursor2 = conn2.cursor()

        conn2.autocommit(1)

        print 'connect to ' + self.host1 + " and " + self.host2
        #---------------------------

        name_list = []
        phone_list = []
        email_list = []

        for keyword in self.group:

            SQL_Select = 'select reg_' + keyword + ' from ' + self.base2_table + keyword
            cursor2.execute(SQL_Select)
            rows = cursor2.fetchall()

            for row in rows:
                if keyword == 'name':
                    name_list.append(row[0])
                if keyword == 'phone':
                    phone_list.append(row[0])
                if keyword == 'email':
                    email_list.append(row[0])

        print len(name_list), name_list
        print len(phone_list), phone_list
        print len(email_list), email_list
        #非正常数据去除
        
        if name_list:
            name_list.pop(0)
        for keyword in ['REDACTED FOR PRIVACY',
                        '******** ******** (see Notes section below on how to view unmasked data)',
                        'Data Protected Data Protected',
                        'Domain Admin',
                        'SLD Admin',
                        'Nexperian Holding Limited',
                        'Registration Private',
                        'Whois Agent',
                        'WhoisGuard Protected',
                        'yinsi baohu yi kai qi(Hidden by Whois Privacy Protection Service)','']:

            if keyword in name_list:
                name_list.remove(keyword)

        if phone_list:
            phone_list.pop(0)
        for item in phone_list:
            if '+86.' not  in item:
                phone_list.remove(item)
        for keyword in ['REDACTED FOR PRIVACY',
                        '+**.***********','']:
            
            if keyword in phone_list:
                phone_list.remove(keyword)

        if email_list:
            email_list.pop(0)
        for keyword in ['Select Contact Domain Holder link at https',
                        'contact via https',
                        'Please query the RDDS service of the Registrar of Record identified in this output for information on how to contact the Registrant, Admin, or Tech contact of the queried domain name.',
                        'contact@privacyprotect.org',
                        'noreply@data-protected.net',
                        'YuMing@YinSiBaoHu.AliYun.com',
                        'privacyprotect@foxmail.com','']:
            
            if keyword in email_list:
                email_list.remove(keyword)

        #print len(name_list), name_list
        #print len(phone_list), phone_list
        #print len(email_list), email_list

        for n in xrange(10):
            i = n + 1
            for name in name_list:
                SQL_Search = 'select domain from ' + self.base1_table + str(i) + ' where reg_name = \'' + name + '\''
                try:
                    print SQL_Search
                except:
                    print "error"
                cursor1.execute(SQL_Search)
                name_domains = cursor1.fetchall()
                for name_domain in name_domains:
                    #print name_domain[0]
                    SQL_Write = 'replace into ' + self.new_table + ' (domain, reg_name) values(\'%s\',\'%s\')'%(name_domain[0], name)
                    try:
                        cursor2.execute(SQL_Write)
                    except:
                        pass

            for phone in phone_list:
                SQL_Search = 'select domain from ' + self.base1_table + str(i) + ' where reg_phone = \'' + phone + '\''
                try:
                    print SQL_Search
                except:
                    print "error"
                cursor1.execute(SQL_Search)
                phone_domains = cursor1.fetchall()
                for phone_domain in phone_domains:
                    #print phone_domain
                    SQL_Write = 'replace into ' + self.new_table + ' (domain, reg_phone) values(\'%s\',\'%s\')'%(phone_domain[0], phone)
                    try:
                        cursor2.execute(SQL_Write)
                    except:
                        pass

            for email in email_list:
                SQL_Search = 'select domain from ' + self.base1_table + str(i) + ' where reg_email = \'' + email + '\''
                try:
                    print SQL_Search
                except:
                    print "error"
                cursor1.execute(SQL_Search)
                email_domains = cursor1.fetchall()
                for email_domain in email_domains:
                    #print email_domain
                    SQL_Write = 'replace into ' + self.new_table + ' (domain, reg_email) values(\'%s\',\'%s\')'%(email_domain[0], email)
                    try:
                        cursor2.execute(SQL_Write)
                    except:
                        pass

        conn1.close()
        conn2.close()
        cursor1.close()
        cursor2.close()


class AnalysisData2():

    def __init__(self):

        print "Init Begin!"

        self.host = '0.0.0.0'
        self.port = 3306
        self.user = 'root'
        self.passwd = ' '
        self.charset = 'utf8'
        self.database = 'idomains_mine_locate'

        self.domain_table = 'whois_reverse_total'

        self.base_table = 'malicious_'
        self.name_table = 'malicious_name'
        self.phone_table = 'malicious_phone'
        self.email_table = 'malicious_email'

        self.group = ['name', 'phone', 'email']


    def main(self):

        #---------------------------
        print 'Begin connect!'
        conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, charset=self.charset, port=self.port)
        cursor = conn.cursor()
        conn.autocommit(1)
        print 'connect to ' + self.host
        #---------------------------

        for keyword in self.group:
            SQL_Select='select reg_' + keyword + ',count(*) from whois_reverse_total group by reg_' + keyword
            cursor.execute(SQL_Select)
            rows = cursor.fetchall()
            for row in rows:
                print row, type(row)
                SQL_Insert='update ' + self.base_table + keyword + ' set reverse_num =%s'%row[1]+' where reg_'+ keyword + '=\'%s\''%row[0]
                print SQL_Insert
                cursor.execute(SQL_Insert)
            print keyword, " is OK!"

        conn.close()
        cursor.close()

class Intable():

    def __init__(self):
        print "Put new_domains into basetable!!!"

        self.host = '0.0.0.0'
        self.port = 3306
        self.user = 'root'
        self.passwd = ' '
        self.charset = 'utf8'
        self.database = 'idomains_mine_locate'

        self.table0 = 'possible_illegal_domains_index'
        self.table1 = 'whois_reverse_total'

        self.group = ['name', 'phone', 'email']

    def main(self):

        #---------------------------
        print 'Begin connect!'
        conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database, charset=self.charset, port=self.port)
        cursor = conn.cursor()
        #conn.autocommit(1)
        print 'connect to ' + self.host
        #---------------------------

        for keyword in self.group:
            sqlget = "select domain from "+self.table1+" where reg_"+keyword+" is not null"
            print sqlget
            cursor.execute(sqlget)
            domains = cursor.fetchall()
            for domain in domains:
                sqlin = "insert into "+self.table0+" (domain,  source) value (\'%s\',\'"%(domain[0])+keyword+"_reverse\')"
                #print sqlin
                print domain
                try:
                    cursor.execute(sqlin)
                except Exception as e:
                    print e, "------------------------------------------"
        conn.commit();

def run():
    #初始从wjx处获取的whois---flag==1
    test1 = initwhois()
    test1.getwhois()


    #二次从cp处获取的whois---flag==0
    test2 = Fakedomain()
    test2.main()
    #失败，外网访问内网、流量被限制（偶尔正常）

    #获取各个reg_name,reg_phone,reg_email以及使用次数
    analysis = AnalysisData()
    analysis.main()

    #反查开始
    begin = searchback()
    begin.main()

    #获取反查后各个reg_name,reg_phone,reg_email以及使用次数
    analysis2 = AnalysisData2()
    analysis2.main()

    #放入基表
    getin = Intable()
    getin.main()



if __name__ == '__main__':
    #初始从wjx处获取的whois---flag==1
    test1 = initwhois()
    test1.getwhois()


    #二次从cp处获取的whois---flag==0
    test2 = Fakedomain()
    test2.main()
    #失败，外网访问内网、流量被限制（偶尔正常）

    #获取各个reg_name,reg_phone,reg_email以及使用次数
    analysis = AnalysisData()
    analysis.main()

    #反查开始
    begin = searchback()
    begin.main()

    #获取反查后各个reg_name,reg_phone,reg_email以及使用次数
    analysis2 = AnalysisData2()
    analysis2.main()

    #放入基表
    getin = Intable()
    getin.main()

