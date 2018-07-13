#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

def selenium_scrape(url):
    # 只能使用系统中已安装浏览器的 Selenium 接口
    # geckodriver.exe 和 chromedriver.exe 均需单独下载
    driver = webdriver.Firefox(executable_path='D:/GreenSoftware/geckodriver.exe')
    #driver = webdriver.Chrome('D:/GreenSoftware/chromedriver.exe')
    driver.get(url)

    # 找到网页界面元素，模拟键盘输入
    driver.find_element_by_id('search_term').send_keys('.')
    # Selenium 的设计初衷是与浏览器交互，而不是修改网页内容，可以使用 Javascript 语句来修改
    js = "document.getElementById('page_size').options[1].text='6'"
    driver.execute_script(js);
    # 单击搜索按钮
    driver.find_element_by_id('search').click()
    # 设置超时时间 - 30 秒，如果要查找的元素没有出现，最多等待三十秒
    driver.implicitly_wait(30)

    links = driver.find_elements_by_css_selector('#results a')
    countries = [link.text for link in links]
    print countries

    # 关闭浏览器
    driver.close()

if __name__ == '__main__':
    selenium_scrape('http://example.webscraping.com/places/default/search')