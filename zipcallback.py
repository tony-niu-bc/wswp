#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import urllib2

from zipfile    import ZipFile
from StringIO   import StringIO

class ZipCallback:

    def __init__(self, zip_url):
        self.zip_url = zip_url

        self.zip_data = urllib2.urlopen(zip_url).read()

        with ZipFile(StringIO(self.zip_data)) as zf:
            for file_name in zf.namelist():
                print file_name
                print zf.open(file_name)

    def __call__(self, file_name, max=10):

        if self.zip_data is not None:
            with ZipFile(StringIO(self.zip_data)) as zf:
                index = 0
                # 按行读取，每次一行
                # for content in csv.reader(zf.open(file_name)):
                # 按字段取值，每次一行
                for num, content in csv.reader(zf.open(file_name)):
                    print 'num = %s, content = %s' % (num, content)

                    index += 1
                    if index >= max:
                        break

if __name__ == '__main__':
    zc = ZipCallback('http://s3.amazonaws.com/alexa-static/top-1m.csv.zip')
    zc('top-1m.csv')
