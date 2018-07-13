#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import PySide classes
import sys
import time

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtWebKit import *

import lxml.html

def hello_world():
    # Create a Qt application
    app = QApplication(sys.argv)
    # Create a Label and show it
    label = QLabel("Hello World")
    label.show()
    # Enter Qt application main loop
    app.exec_()
    sys.exit()

def js_dynamic(url):
    app  = QApplication([])
    wv   = QWebView()
    loop = QEventLoop()

    wv.loadFinished.connect(loop.quit)
    wv.load(QUrl(url))

    loop.exec_()

    html = wv.page().mainFrame().toHtml()
    tree = lxml.html.fromstring(html)

    # pip install cssselect
    return tree.cssselect('#result')[0].text_content()

def form_submit(url, isVisible=True):
    app  = QApplication([])
    wv   = QWebView()
    loop = QEventLoop()

    if isVisible:
        wv.show()

    wv.loadFinished.connect(loop.quit)
    wv.load(QUrl(url))

    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(60000)

    loop.exec_()

    if timer.isActive():
        # 下载成功
        timer.stop()
    else:
        # 超时
        print 'Request timed out: ' + url

    frame = wv.page().mainFrame()
    frame.findFirstElement('#search_term').setAttribute('value', '.')
    frame.findFirstElement('#page_size').findFirst('option[selected]').setPlainText('6')
    frame.findFirstElement('#search').evaluateJavaScript('this.click()')

    elements = None
    deadline = time.time() + 60
    while (time.time() < deadline) and (not elements):
        app.processEvents()
        elements = frame.findAllElements('#results a')
        time.sleep(1)

    countries = [e.toPlainText().strip() for e in elements]
    print countries

    # 注释掉如下这句程序直接退出
    #app.exec_()

if __name__ == '__main__':
    #print js_dynamic('http://example.webscraping.com/dynamic.html')
    form_submit('http://example.webscraping.com/places/default/search')