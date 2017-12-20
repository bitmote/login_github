# -*- coding: utf-8 -*-
import scrapy


class LoginSpider(scrapy.Spider):
    name = 'login'
    allowed_domains = ['github.com']
    start_urls = ['http://www.github.com/']
    headers = {
        'User_Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    }

    login_url = 'https://github.com/login'
    session_url = 'https://github.com/session'

    def parse(self,response):
        print 'url,',response.url
        print 'status',response.status
        print 'headers',response.headers
        print 'request',response.request
        print 'meta',response.meta


    # def start_requests(self):
    #     return [scrapy.Request(url = self.login_url,headers = self.headers,callback=self.parse_session)]


    def parse_session(self,response):
        token = response.xpath('//input[@name = "authenticity_token"]/@value').extract_first()
        post_data = {
            'commit': 'Sign in',
            'utf8':'✓',
            'authenticity_token':token,
            'login':'bitmote',
            'password':'github2017'
        }
        return [scrapy.FormRequest(url=self.session_url, formdata=post_data, headers=self.headers, callback=self.check_login)]

    def check_login(self,response):
        #<strong class="css-truncate-target">bitmote</strong>
        js = response.xpath('//strong[@class="css-truncate-target"]/text()').extract_first()

        if js:
            print js,'login succeed!'
        else:
            print 'login failed!'