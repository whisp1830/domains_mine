# -*- coding: utf-8 -*-
"""
功能：恶意域名检测
作者：吴晓宝
日期:2018-5-16
"""
import sys
import time
from driverhandler import DriverHandler
from selenium.webdriver.common.keys import Keys
from settings import DRIVER_TYPE
import database.mysql_operation

mysql_conn = database.mysql_operation.MysqlConn('0.0.0.0','root','','idomains_mine_locate','utf8')

class DetectionTools(DriverHandler):

    def __init__(self,*args,**kwargs):

        self.tool_name = args[0]
        if len(args)<1 or self.tool_name not in ('baidu','tencent'):
            print "paras is absent or error!"
            sys.exit(-1)
        driver_type= args[1] if len(args)>1 else(DRIVER_TYPE)
        print driver_type
        DriverHandler.__init__(self,driver_type,**kwargs)

        self.base_urls = {
            'baidu':'http://bsb.baidu.com/diagnosis',
            'tencent':'https://guanjia.qq.com/online_server/result.html?url=qq.com'
        }
        self.button_ids={
            'baidu': 'url',
            'tencent': 'search_site'
        }
        self.counter = 0
        self.enable=True
        self.final_result=""
        self.open_detect_web()

    def open_detect_web(self):
        """
        打开检测页
        :return: 
        """
        url=self.base_urls[self.tool_name]
        count = 0
        while self.enable:
            count+=1
            print "the %dth try open detect web"%count
            if self.open_web(url):
                break

    def main(self,item):
        """
        检测恶意性主程序
        :param item:url/domain 
        :return: result
        """
        self.final_result = ""
        self.counter+=1
        self.input_item(item)
        if self.enable:self.extract_result()
        if not self.enable or self.counter%50==0:
            self.destory_driver()
            self.create_driver()
            self.enable=True
            self.open_detect_web()

        return self.final_result

    def input_item(self,item):
        """
        模拟浏览器输入待检测url/domain
        :param item: url/domain
        :return: 
        """
        try:
            self.driver.find_element_by_id(self.button_ids[self.tool_name]).clear()
            self.driver.find_element_by_id(self.button_ids[self.tool_name]).send_keys(item+Keys.ENTER)
            time.sleep(self.wait_time)
        except Exception,e:
            self.enable = False
            print "click error:",str(e)

    def extract_result(self):

        if self.tool_name=="baidu":
            try:
                res = self.driver.find_elements_by_xpath('//*[@id="result-icon"]/div')
            except Exception, e:
                self.enable = False
                print "xpath error:", str(e)
            else:
                if len(res) != 0:
                    result = res[0].get_attribute('class').strip()
                    if result:
                        if result == "result_safety":
                            self.final_result = "安全".decode("utf8")
                        elif result == "result_danger":
                            self.final_result = "危险".decode("utf8")
                        else:
                            self.final_result = "未知".decode("utf8")
        else:
            MAX_TIME = 4
            waiting_result = "正在检测...".decode("utf8")
            xpath='//*[@id="score_img"]/span'
            try:
                res = self.driver.find_elements_by_xpath(xpath)
            except Exception,e:
                self.enable = False
                print "xpath error:",str(e)
            else:
                if len(res) != 0:
                    result = res[0].text.strip()
                    while result == waiting_result and MAX_TIME > 0:
                        time.sleep(self.wait_time)
                        MAX_TIME -= 4
                        result = self.driver.find_elements_by_xpath(xpath)[0].text.strip()
                    if MAX_TIME!=0 and result:
                        if result.find("危险".decode("utf8")) != -1:
                            if "赌博".decode("utf8") in result:
                                self.final_result = "赌博".decode("utf8")
                            elif "色情".decode("utf8") in result:
                                self.final_result = "色情".decode("utf8")
                            elif "钓鱼".decode("utf8") in result:
                                self.final_result = "钓鱼".decode("utf8")
                            elif "欺诈".decode("utf8") in result:
                                self.final_result = "欺诈".decode("utf8")
                            else:
                                self.final_result = "非法内容".decode("utf8")
                        elif result.find("未知".decode("utf8")) != -1:
                            self.final_result = "未知".decode("utf8")
                        else:
                            self.final_result = "安全".decode("utf8")

def exper(item,tool_name='baidu',driver_type='phantomjs'):
    """
    '137133.com'
    :param item: 
    :return: 
    """
    dt=DetectionTools(tool_name,driver_type)
    result=dt.main(item)
    print "this domain is a %s website" % result
    dt.destory_driver()

if __name__ == "__main__":
    sql = "SELECT domain from possible_illegal_domains_index;"
    list_to_detect = list(mysql_conn.exec_readsql(sql))
    print list_to_detect
    
    #exper('http://00000yd.com/','tencent')#'0b33.com''00000e.com'