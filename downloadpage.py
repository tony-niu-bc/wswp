#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2, urlparse, robotparser, socks, socket, ssl
import re
import itertools
import time, datetime

class DownloadPage:

    # 下载指定页面
    def download(self, url, proxy=None, user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko', num_retries=2):
        print "It's downloading: ", url
        #print "Whose user agent: ", user_agent

        headers = {'User-agent': user_agent}
        request = urllib2.Request(url, headers = headers)

        try:
            if proxy is not None:
                print 'Use proxy read web page: ', proxy
                # use a SOCKS 4/5 proxy with urllib2 # "代理IP", 代理端口
                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy[0], proxy[1])
                socket.socket = socks.socksocket

            # 判断是不是 https 请求
            #print type(request.get_type())
            #print request.get_type()
            if request.get_type() == 'https':
                #print 'request.get_type(): https'
                # Python 升级到 2.7.9 之后引入了一个新特性，当使用urllib.urlopen打开一个 https 链接时，会验证一次 SSL 证书。
                # 而当目标网站使用的是自签名的证书时就会抛出一个 urllib2.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:581)> 的错误消息，
                # 详细信息可以在这里查看（https://www.python.org/dev/peps/pep-0476/）
                # 解决办法一 - 全局取消证书验证：
                #ssl._create_default_https_context = ssl._create_unverified_context

                # 解决办法二 - 使用ssl创建未经验证的上下文：
                context = ssl._create_unverified_context()
                html = urllib2.urlopen(request, context=context).read()
            else:
                #print 'request.get_type(): http'
                html = urllib2.urlopen(request).read()

        except urllib2.URLError as e:
            print "Error reason:", e.reason
            html = None

            if hasattr(e, 'code'):
                print "Error code:", e.code

                if (0 < num_retries) and (500 <= e.code < 600):
                    return self.download(url, proxy, user_agent, num_retries - 1)

        return html

    # 分析 sitemap.xml 文件下载页面
    def crawl_sitemap(self, url):
        sitemap = self.download(url)

        #print sitemap

        links = re.findall('<loc>(.*?)</loc>', sitemap)

        print 'The list of site links:'
        for link in links:
            print link

            # 下载指定链接页面
            #print download(link)

    # 按页面 ID 顺序下载页面
    def iterate_pageid(self, url, max_skip=5):
        skip_num = 0
        for id in itertools.count(1):
            link = url % id
            html = self.download(link)

            if html is None:
                skip_num += 1

                print 'Have not downloaded: %s\n' % link

                if max_skip <= skip_num:
                    break
            else:
                # 跳过间隔的 id 又可下到新页面时清零
                skip_num = 0
                print 'Have downloaded: %s\n' % link

    # 分析页面中的链接
    def get_links(self, html):
        link_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
        return link_regex.findall(html)

    # 遍历页面中的指定链接来下载页面
    def link_crawler(self, domain, link_regex=None, rp=None, max_deep=-1):
        crawl_queue = [domain]
        seen_set = {domain: 0}

        while crawl_queue:
            url = crawl_queue.pop()

            if (rp is not None) and (not rp.can_fetch(url)):
                print "Can't fetch: ", url
                continue

            html = self.download(url)

            if html is None:
                continue

            deep = seen_set[url]
            print 'url = %s\ndeep = %d' % (url, deep)
            if (-1 == deep) or (deep != max_deep):
                for link in self.get_links(html):
                    #print 'Obtain link: ', link
                    if (link_regex is not None) and (re.match(link_regex, link)):
                        link = urlparse.urljoin(domain, link)
                        #print 'Join link: ', link

                        if link not in seen_set:
                            print 'Insert link: ', link
                            seen_set[link] = deep + 1
                            crawl_queue.append(link)

# 分析 robots.txt
class RobotstxtParse:
    __rp = None
    __user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'

    def set_robotstxt(self, robotstxt, agent='Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'):
        self.__rp = robotparser.RobotFileParser()
        self.__rp.set_url(robotstxt)
        self.__rp.read()
        self.set_rp_agent(agent)

    def get_robotparser(self):
        if self.__rp is None:
            raise ValueError('RobotFileParser object is None!')

        return self.__rp

    def set_rp_agent(self, user_agent):
        if isinstance(user_agent, str):
            self.__user_agent = user_agent

    def can_fetch(self, url):
        return self.get_robotparser().can_fetch(self.__user_agent, url)

# 下载限速（两次下载之间添加延时） - 如果我们爬取网站的速度过快，就会面临被封禁或是造成服务器过载的风险
class Throttle:

    def __init__(self, delay):
        # 两次下载间的延时时长
        self.delay = delay
        # 最后一次访问的时间戳
        self.domains = {}

    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        print 'url = %s\ndomain = %s, last_accessed = %s' % (url, domain, str(last_accessed))

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds

            if sleep_secs > 0 :
                time.sleep(sleep_secs)

        self.domains[domain] = datetime.datetime.now()

# 测试 Throttle 功能
#throttle = Throttle(2)
#for x in [1,2]:
#    throttle.wait('http://www.example.com')
#    print datetime.datetime.now()

# 判断某页面用某代理名是否可以下载
# User-agent: Baiduspider
# Disallow: /baidu
# Disallow: /s?
# Disallow: /ulink?
# Disallow: /link?
# Disallow: /home/news/data/
# rp = RobotstxtParse()
# rp.set_robotstxt('https://www.baidu.com/robots.txt', 'Baiduspider')
# print rp.get_robotparser()
#
# print rp.can_fetch('https://www.baidu.com/s?wd=今日新鲜事')
# print rp.can_fetch('http://news.baidu.com/?tn=news')

# dp = DownloadPage()

# 分析站点地图
# dp.crawl_sitemap('http://www.zhxfei.com/sitemap.xml')

# 遍历页面ID来下载页面
# dp.iterate_pageid('http://example.webscraping.com/places/default/index/%d')

# 遍历页面中的链接来下载页面
# dp.link_crawler('http://www.zhxfei.com', '/\d\d\d\d/\d\d/\d\d', rp, 2)

# 通过代理下载 google 页面
# print dp.download('https://www.google.com/', ('localhost', 2530))
