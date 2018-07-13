#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html, lxml.etree
import savecsv

class ScrapeData:
    def __init__(self):
        self.csv = savecsv.SaveCSV('vegetable_price')

    # 格式化 html 文本内容
    def __format_html(self, html):
        return lxml.html.tostring(lxml.html.fromstring(html), pretty_print=True)

    def csv_bj_vegetable_price(self, html, firstpage=True):
        # 先确保 html 经过了 utf-8 解码，即code = html.decode('utf-8', 'ignore')，
        # 否则会出现解析出错情况。
        # 因为中文被编码成utf-8之后变成 '/u2541' 之类的形式，lxml一遇到 “/” 就会认为其标签结束。
        page = lxml.etree.HTML(self.__format_html(html.decode('utf-8')))
        # 选取所有拥有名为 class 的属性且值为 hq_table 的 table 元素。
        table = page.xpath("//table[@class='hq_table']/tr")

        # 遍历 table 下的所有 tr
        index = 0
        for tr in table:
            # 非第一页则不再分析标题
            if (not firstpage) and (0 == index):
                index = 1
                continue

            index += 1
            self.csv(self.__traverse_tr(tr))

    # 遍历 tr 下的所有 td
    def __traverse_tr(self, tr):
        index = 0
        row = []
        for td in tr:
            # 品名/最低价/平均价/最高价/规格/单位/发布日期
            if index >= 7:
                break

            index += 1
            print 'td: ', td.text.encode('utf8').strip()
            row.append(td.text.encode('utf8').strip())

        return row
