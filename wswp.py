#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

from scrapedata   import ScrapeData
from downloadpage import DownloadPage

dp = DownloadPage()
#dp.link_crawler('http://www.xinfadi.com.cn/marketanalysis/0/list/1.shtml', '/marketanalysis/0/list/\d+.shtml', None, 1)

# 读取新发地 散鸡蛋 2000-01-01 ~ 2036-12-31 全部价格
seedurl = 'http://www.xinfadi.com.cn/marketanalysis/0/list/1.shtml?prodname=散鸡蛋&begintime=2000-01-01&endtime=2036-12-31'
html = dp.download(seedurl)
maxid = 1

if html is None:
    try:
        sys.exit(1)
    except:
        print 'seedurl download failed!'

sd = ScrapeData()

sd.csv_bj_vegetable_price(html)

# 找到 尾页 的id
for link in dp.get_links(html):
    if re.match('/marketanalysis/0/list/\d+.shtml\?prodname=散鸡蛋&begintime=2000-01-01&endtime=2036-12-31', link):
        strs = str.split(link, '/')
        strs = strs[-1].split('.')
        print 'link: ', link
        maxid = max(maxid, int(strs[0]))

# 按 id 顺序下载网页并分析页面内容
print 'maxid = ', maxid
for id in range(2, maxid + 1):
    link = 'http://www.xinfadi.com.cn/marketanalysis/0/list/%d%s' % (id, '.shtml?prodname=散鸡蛋&begintime=2000-01-01&endtime=2036-12-31')
    html = dp.download(link)
    sd.csv_bj_vegetable_price(html, False)
