# -*- coding: utf-8 -*-

import os
import sys
import time
import commands
from selenium import webdriver
from settings import DRIVER_SETTINGS
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from settings import HEADLESS,LOAD_PICTURE

class DriverHandler(object):
    """
    driverhandler:无界面web驱动柄
    """
    def __init__(self,*args,**kwargs):
        """
        最长加载时间max_time
        等待时间wait_time
        图片是否加载loading_pic
        使用的驱动:默认chrome
        :param args: 
        :param kwargs: 
        """
        self.driver_type='chrome'
        if len(args)>0:self.driver_type=args[0]
        if self.driver_type == "phantomjs":
            self.driver_path = DRIVER_SETTINGS['phantomjs_path']
        else:
            self.driver_path = DRIVER_SETTINGS['chrome_path']
        print self.driver_type
        if self.driver_type not in("chrome","phantomjs"):
            print "Hasn't this driver type!"
            sys.exit(-1)
        self.max_time=self.set_default(kwargs.get('max_time'),60)
        self.wait_time=self.set_default(kwargs.get('wait_time'),3)
        self.loading_pic=self.set_default(kwargs.get('loading_pic'),LOAD_PICTURE)
        self.set_headless= HEADLESS
        self.create_driver()

    def create_driver(self,timeout=None):
        """
        创建驱动柄
        :param timeout: 
        :return: 
        """
        max_time=self.max_time if not timeout else(timeout)
        if self.driver_type=="phantomjs":
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.loadImages"] = self.loading_pic
            self.driver = webdriver.PhantomJS(
                executable_path=self.driver_path,
                desired_capabilities=dcap
            )
        else:
            dcap = DesiredCapabilities.CHROME
            dcap['loggingPrefs'] = {'performance': 'ALL'}
            chromeOptions = webdriver.ChromeOptions()
            if self.set_headless:
                os.environ["webdriver.chrome.driver"] = self.driver_path
                chromeOptions.add_argument('--headless')
            #1:允许所有图片；2：阻止所有图片；3：阻止第三方服务器图片
            images_flag=1 if self.loading_pic else(2)
            prefs = {
                "profile.managed_default_content_settings": {
                    'images': images_flag
                }
            }
            chromeOptions.add_experimental_option("prefs", prefs)
            self.driver = webdriver.Chrome(
                executable_path=self.driver_path,
                chrome_options=chromeOptions,
                desired_capabilities=dcap
            )
        self.driver.set_page_load_timeout(max_time)
        self.driver.set_script_timeout(max_time)

    def destory_driver(self):
        """
        关闭/销毁驱动
        :return: 
        """
        try:
            self.driver.quit()
        except Exception,e:
            print "quit driver error:",str(e)
            print "current pid is %d" % os.getpid()
            cur_pid = os.getpid()
            cmd = 'ps -efw|grep {driver_type}|grep -v grep|cut -c 9-15,16-21' \
                  ''.format(driver_type=self.driver_type)
            output = commands.getoutput(cmd)
            lines = output.split('\n')
            pid_list = []
            for line in lines:
                tup = tuple([item.strip() for item in line.split(' ') if item.strip() != ''])
                pid, ppid = tup
                if ppid == str(cur_pid):
                    print "kill " + str(pid)
                    pid_list.append(pid)
            pids = ' '.join(pid_list)
            commands.getoutput('kill -9 ' + pids)
            print "kill over!"
        else:
            print "quit driver successfully"

    def open_web(self,url):
        """
        打开页面
        :param url: 
        :return: 
        """
        try:
            self.driver.get(url)
            # self.driver.implicitly_wait(self.wait_time)
            time.sleep(self.wait_time)
        except Exception,e:
            if str(e).find('timeout')!=-1:
                return -1#超时
            else:
                return 0#异常
        else:
            return 1#正常

    def set_default(self,value, default):
        """
        将None置为默认值
        :param value: 
        :param default: 
        :return: 
        """
        return default if not value else(value)