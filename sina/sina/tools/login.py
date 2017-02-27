#! -*- coding:utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

URL = 'http://weibo.com/login.php'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
COOKIE_PATH = BASE_PATH+'/cookie.txt'
SCREENSHOT_PATH = BASE_PATH+'/SCREENSHOT_%s.jpg'
USERAGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/602.4.8 (KHTML, like Gecko) Version/10.0.3 Safari/602.4.8'

class Sina(object):
    def __init__(self, username, password):
        self.username, self.password = username, password
        desired_capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        desired_capabilities['phantomjs.page.settings.userAgent'] = USERAGENT
        self.http_client = webdriver.PhantomJS(desired_capabilities=desired_capabilities)
        self.http_client.maximize_window()
        self.cookie_path = COOKIE_PATH+self.username

    def __del__(self):
        self.http_client.quit()

    def login(self):
        ch_c = self.check_cookie()
        if ch_c: return ch_c

        self.http_client.get(URL); time.sleep(3)
        self.http_client.get_screenshot_as_file(SCREENSHOT_PATH %('a'))

        self.http_client.find_element_by_class_name('gn_login_list').find_element_by_xpath('//a[@node-type="loginBtn"]').click(); time.sleep(3)
        self.http_client.get_screenshot_as_file(SCREENSHOT_PATH %('b'))
        
        username_key = self.http_client.find_element_by_xpath('//div[@class="item username input_wrap"]/input')
        username_key.clear()
        username_key.send_keys(self.username)
        password_key = self.http_client.find_element_by_xpath('//div[@class="item password input_wrap"]/input')
        password_key.clear()
        password_key.send_keys(self.password)
        submit_key = self.http_client.find_element_by_xpath('//div[@class="item_btn"]/a')
        submit_key.click()

        time.sleep(5)
        self.http_client.get_screenshot_as_file(SCREENSHOT_PATH %('c'))

        #验证码处理
        try:
            self.http_client.find_element_by_xpath('//input[@class="W_input W_input_focus"]')
        except:
            pass
        else:
            url = self.http_client.find_element_by_xpath('//img[@action-type="btn_change_verifycode"][@width="100"]').get_attribute('src')
            self.http_client.get_screenshot_as_file(SCREENSHOT_PATH %('d'))
            verifycode = raw_input("raw_input_%s: " %url)
            verifycode_key = self.http_client.find_element_by_xpath('//*[@class="Bv6_layer "]/div[2]/div[3]/div[3]/div[4]/input')
            verifycode_key.clear()
            verifycode_key.send_keys(verifycode)
            self.http_client.get_screenshot_as_file(SCREENSHOT_PATH %('f'))
            submit_key = self.http_client.find_element_by_xpath('//div[@class="item_btn"]/a')
            submit_key.click()
            time.sleep(5)
            self.http_client.get_screenshot_as_file(SCREENSHOT_PATH %('g'))
   
        if '我的首页' in self.http_client.title: login_s = 1
        else: login_s = 0

        if login_s:
            with open(self.cookie_path, 'w') as f: f.write(json.dumps(self.http_client.get_cookies()))
            return self.http_client.get_cookies()
        else: return {}

    def check_cookie(self):
        try:
            with open(self.cookie_path) as f: cookies = json.loads(f.read())
        except:
            return {}
        s = requests.Session()
        for cookie in cookies: s.cookies.set(cookie['name'], cookie['value'])
        if '我的首页' in s.get("http://weibo.com").text[:3000]: return cookies
        return {}

if __name__ == '__main__':
    sina = Sina(sys.argv[1], sys.argv[2])
    print sina.login()
