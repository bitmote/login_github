# -*- coding: utf-8 -*-
import scrapy
from login_github.items import  LoginGithubItem

class LoginSpider(scrapy.Spider):
    name = 'login'
    allowed_domains = ['github.com']
    start_urls = ['http://www.github.com/']
    headers = {
        'User_Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
    }
    #只爬一千个用户,在爬取过程中存在一个问题就是由于搜索一个用户以后，接着搜索他的follower和following，对于他的follower页面也是如此，将
    #很多用户页面存入，但是只处理第一个，然后再进入第一个的follower和following，永远是缓存当前的所有follower，但是只进入第一个，因此，这是
    #先深搜索，先广搜索的算法如下
    user_num = 0
    login_url = 'https://github.com/login'
    session_url = 'https://github.com/session'
    base_url = 'https://github.com'
    user_list = []
    def parse_user(self,response):
        #写出人名、自我介绍、location，following总数，follower总数
        #<span class="p-nickname vcard-username d-block" itemprop="additionalName">mioaowuyunjiang</span>
        #<span class="p-name vcard-fullname d-block" itemprop="name">喵呜运酱</span>
        #先不考虑去重
        self.user_num += 1
        print 'number=  ',self.user_num
        if self.user_num >= 200:
            return
        item = LoginGithubItem()
        name = response.xpath('//span[@class = "p-name vcard-fullname d-block"]/text()').extract_first()
        id = response.xpath('//span[@class = "p-nickname vcard-username d-block"]/text()').extract_first()
        item['full_name'] = name
        item['additional_name'] = id
        yield item
        follower_url = response.url + '?tab=followers'
        following_url = response.url + '?tab=following'
        #yield scrapy.Request(follower_url, callback=self.parse_follower)
       # yield scrapy.Request(following_url, callback=self.parse_following)


    def parse_follower(self,response):

        has_next = False
        if self.user_num >= 200:
            return
        follower_content = response.xpath('//div[@class="position-relative"]')
        #没有follower
        if follower_content.xpath('div[@class="blankslate mt-4"]'):

            return
        else:
            followers = follower_content.xpath('div[@class="d-table col-12 width-full py-4 border-bottom border-gray-light"]')
            next_page = follower_content.xpath('div[@class="paginate-container"]')
            for follower in followers:
                user_url = self.base_url + follower.xpath('div[2]/a/@href').extract_first()
                self.user_list.append(user_url + '?tab=followers')
                yield scrapy.Request(user_url,callback=self.parse_person,priority = 2)
            if next_page:
                next_url = next_page.xpath('div[@class = "pagination"]/a')
                print 'user  ',response.url
                print 'next_url',next_url
                for page in next_url:
                    if page.xpath('text()').extract_first() == u'Next':
                        has_next = True
                        next_page_url = page.xpath('@href').extract_first()
                        print 'nextpage ',next_page_url
                        yield scrapy.Request(next_page_url,callback=self.parse_follower,priority=1)


        print 'length  ,',len(self.user_list)
        #如果上述的网页都爬取完毕，再执行下述的操作
        if has_next == False:
            if self.user_list:
                print 'while part!!!!'
                user_follower_url = self.user_list.pop(0)
                print user_follower_url
                yield scrapy.Request(user_follower_url,callback=self.parse_follower,priority=0)




    def parse_person(self,response):
        self.user_num += 1
        print 'number=  ',self.user_num
        if self.user_num >= 200:
            return
        item = LoginGithubItem()
        name = response.xpath('//span[@class = "p-name vcard-fullname d-block"]/text()').extract_first()
        id = response.xpath('//span[@class = "p-nickname vcard-username d-block"]/text()').extract_first()
        item['full_name'] = name
        item['additional_name'] = id
        yield item

    def parse_following(self,response):

        if self.user_num >= 100:
            return
        follower_content = response.xpath('//div[@class="position-relative"]')
        if follower_content.xpath('div[@class="blankslate mt-4"]'):
            return
        else:
            followers = follower_content.xpath('div[@class="d-table col-12 width-full py-4 border-bottom border-gray-light"]')
            next_page = follower_content.xpath('div[@class="paginate-container"]')
            for follower in followers:
                user_url = self.base_url + follower.xpath('div[2]/a/@href').extract_first()
                yield scrapy.Request(user_url,callback=self.parse_user)
            if next_page:
                next_url = next_page.xpath('div[@class = "pagination"]/a')
                for page in next_url:
                    if page.xpath('text()') == u'Next':
                        next_page_url = page.xpath('@href').extract_first()
                        yield scrapy.Request(next_page_url,callback=self.parse_following)




    def start_requests(self):
        return [scrapy.Request(url = self.login_url,headers = self.headers,callback=self.parse_session)]


    def parse_session(self,response):
        token = response.xpath('//input[@name = "authenticity_token"]/@value').extract_first()
        post_data = {
            'commit': 'Sign in',
            'utf8':'✓',
            'authenticity_token':token,
            'login':'yourid',
            'password':'yourpasswd'
        }
        return [scrapy.FormRequest(url=self.session_url, formdata=post_data, headers=self.headers, callback=self.check_login)]

    def check_login(self,response):

        js = response.xpath('//strong[@class="css-truncate-target"]/text()').extract_first()

        if js:
            print js,'login succeed!'
        else:
            print 'login failed!'
        profile_url = 'https://github.com/frogoscar'
        follower_url = profile_url + '?tab=followers'
        following_url = profile_url + '?tab=following'
        #yield scrapy.Request(profile_url,callback=self.parse_user)
        yield scrapy.Request(follower_url,callback=self.parse_follower)
        #yield scrapy.Request(following_url,callback=self.parse_following)


