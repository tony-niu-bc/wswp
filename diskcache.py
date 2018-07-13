#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import pickle
import zlib
import re
import urlparse
from datetime import datetime, timedelta

# 磁盘缓存有三大弊端：
# 1. 文件名易重复(Hask值作为文件名可以解决)
# 2. 文件夹下的文件数量有限，FAT32 最大 65535 个文件，ext4 大于 1500 万个文件
# 3. 多个缓存网页合并一个文件中，使用类似 B+ 树的算法进行索引，不如用 NoSQL 数据库
class DiskCache:

    def __init__(self, cache_dir='cache', max_length=255, expires=timedelta(days=30)):
        self.cache_dir  = cache_dir
        self.max_length = max_length
        self.expires    = expires

    # 根据 URL 从磁盘上加载数据
    def __getitem__(self, url):
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                result, timestamp = pickle.loads(zlib.decompress(fp.read()))

                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')

                return result
        else:
            raise KeyError(url + ' does not exist')

    # 根据 URL 保存数据到磁盘上
    def __setitem__(self, url, result):
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        timestamp = datetime.utcnow()
        data = pickle.dumps((result, timestamp))

        with open(path, 'wb') as fp:
            fp.write(zlib.compress(data))

    # 判断 时间戳 是否过期
    def has_expired(self, timestamp):
        return datetime.utcnow() > timestamp + self.expires

    # URL 转系统文件路径
    def url_to_path(self, url):
        components = self.split_url(url, 0)
        path = components.path

        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'

        filename = self.limit_length(self.format_url(components.netloc + path + '_' + components.query))

        return os.path.join(self.cache_dir, filename)

    # 不同操作系统的非法文件名字符均不同：
    # Linux    ext3/4    / 和 \0
    # OS X     HFs Plus  : 和 \0
    # Windows  NTFS      \、/、?、:、*、"、>、< 和 |
    # 为了保证在不同文件系统中文件路径都是安全的，
    # 只能包含数字、字母和基本符号，并将其他字符替换为下划线
    def format_url(self, url):
        # utf8 下，每个汉字占据 3 个字符位置，正则式为[\x80-\xff]{3}
        return re.sub('[^\x80-\xff/0-9a-zA-Z\-.,;_]', '_', url)

    # 文件名及其父目录的长度需要限制在255个字符以内
    def limit_length(self, filename, len=255):
        return os.path.sep.join(segment[:len] for segment in filename.split('/'))

    # 分解URL
    # scheme = 1 netloc = 2 path = 4 query = 8 fragment = 16
    # http://www.xinfadi.com.cn/marketanalysis/0/list/1.shtml?prodname=散鸡蛋&begintime=2000-01-01&endtime=2036-12-31
    # scheme =  http
    # netloc =  www.xinfadi.com.cn
    # path =  /marketanalysis/0/list/1.shtml
    # query =  prodname=散鸡蛋&begintime=2000-01-01&endtime=2036-12-31
    # fragment =
    def split_url(self, url, flag=1):
        if   flag == 1:
            return urlparse.urlsplit(url).scheme
        elif flag == 2:
            return urlparse.urlsplit(url).netloc
        elif flag == 4:
            return urlparse.urlsplit(url).path
        elif flag == 8:
            return urlparse.urlsplit(url).query
        elif flag == 16:
            return urlparse.urlsplit(url).fragment
        else:
            return urlparse.urlsplit(url)
