#! -*- coding:utf-8 -*-
from __future__ import division

import math
import json
import scrapy
from sina.tools.login import Sina
from scrapy.selector import Selector

class DmozSpider(scrapy.spiders.Spider):
    name = 'sina_follow'
    allowed_domains = ['weibo.com']
    follow_url = 'http://weibo.com/%s/follow'
    follow_page_id_url = 'http://weibo.com/p/%s/myfollow?t=1&Pl_Official_RelationMyfollow__93_page=%d'

    def __init__(self, username = None, password = None, *args, **kwargs):
        super(DmozSpider, self).__init__(*args, **kwargs)
        self.username, self.password = username, password

    def start_requests(self):
        sina_login = Sina(self.username, self.password)
        cookies = sina_login.login()
        assert cookies != {}
        yield scrapy.Request('http://weibo.com', cookies=cookies, callback=self.init_parse)

    def init_parse(self, response):
         assert '我的首页' in response.body[:3000]
         self.uid =  response.url.split('/')[4]
         yield scrapy.Request(self.follow_url %self.uid, callback=self.follow_parse)

    def follow_parse(self, response):
        self.page_id    = response.selector.re("""\['page_id'\]='(.*?)'""")[0]
        self.follow_sum = response.selector.re("""attach S_txt1..>(.*?)<""")[0]
        page_num = math.ceil(int(self.follow_sum)/30)
        for pn in xrange(int(page_num)):
            yield scrapy.Request(self.follow_page_id_url %(self.page_id, pn+1), callback=self.follow_page_id_parse)

    def follow_page_id_parse(self, response):
        for screen_name in response.selector.re("""screen_name=(.*?)&sex"""):
            print screen_name
        
