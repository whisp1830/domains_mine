#-*- coding: utf8 -*-

import os
import time
from db_conn import DBConn
from detectmalicious import DetectionTools
from multi_process import multi_run
from settings import LOAD_SQL_TABLE,UPDATE_SQL_TABLE

def load_items(start=0,num=-1):

    if num==-1:
        num=int(1e8)
    LOAD_SQL = "SELECT domain FROM {TABLE_NAME} " \
               "WHERE {constraint} LIMIT {START},{LIMIT}" \
               "".format(TABLE_NAME=LOAD_SQL_TABLE,constraint="result_flag is null",START=start,LIMIT=num)  # sql语句导出数据
    db=DBConn()
    db.get_mysql_conns(num=1)
    db.exec_sql(LOAD_SQL)
    result=db.mysql_cur.fetchall()
    items=[item[0] for item in result]
    db.close_mysql_conns()
    print "load %s items"%len(items)

    return items

def task(process_id,share_q):

    print 'Run task %s (%s)...' % (process_id, os.getpid())
    UPDATE_SQL="UPDATE {TABLE_NAME} SET result_flag=%s,illegal_type=%s WHERE domain=%s".format(TABLE_NAME=UPDATE_SQL_TABLE)
    start = time.time()
    db=DBConn()
    db.get_mysql_conns(num=1)
    dt = DetectionTools('tencent')
    count=0
    while (isinstance(share_q,list) and len(share_q)) or (hasattr(share_q,'empty') and not share_q.empty()):
        count+=1
        if isinstance(share_q,list):
            item = share_q.pop(0)
        else:
            item = share_q.get()
        domain=item
        print "{0}:{1}".format(count,domain)
        result=dt.main(domain)
        if result == "未知".decode("utf8"):
            is_illegal = -1
        elif result == "安全".decode("utf8"):
            is_illegal = 0
        else:
            is_illegal = 1
        print "this domain is a %s website" % result
        db.exec_sql(UPDATE_SQL,data=(is_illegal,result,domain))
        print count
        if count%10==0:
            print "commit %d records"%count
            db.mysql_conn.commit()
    print "commit %d records" % count
    db.mysql_conn.commit()
    db.close_mysql_conns()
    dt.destory_driver()
    del dt,db
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (process_id, (end - start))

def run():
    #如有必要可以根据表结构更改LOAD_SQL与UPDATE_SQL,以及settings中的配置
    multi_run(source_data=load_items(start=0,num=10000), task=task, process_num=5, mode=1)


if __name__ == '__main__':
    run()