#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lxml.html
import cookielib
import urllib2
import urllib
import mechanize
import pprint
import pytesseract
import string

from io  import BytesIO
from PIL import Image

def parse_form(html):
    tree = lxml.html.fromstring(html)
    data = {}

    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')

    print data
    print '--------'
    pprint.pprint(data)

    return data

def mechanize_form(login_url, login_email, login_password):
    br = mechanize.Browser()
    br.open(login_url)
    br.select_form(nr=0)
    br['email'] = login_email
    br['password'] = login_password

    response = br.submit()

    br.open('http://example.webscraping.com/places/default/edit/Aland-Islands-2')
    br.select_form(nr=0)
    br['population'] = str(int(br['population']) + 1)
    br.submit()

def main(login_url, login_email, login_password):
    cj = cookielib.CookieJar()
    # 当普通用户加载登录表单时，服务器端给定 表单ID 来判断表单是否已经提交过，
    # 表单ID(如：029lec65-9332-426e-b6al-d97b3a2bl2f8)会保存在 cookie 中，
    #
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(login_url).read()

    data = parse_form(html)
    data['email'] = login_email
    data['password'] = login_password

    encoded_data = urllib.urlencode(data)

    request = urllib2.Request(login_url, encoded_data)

    response = opener.open(request)
    print response.geturl()

def get_captcha(html):
    tree = lxml.html.fromstring(html)

    img_data = tree.cssselect('div#recaptcha img')[0].get('src')
    img_data = img_data.partition(',')[-1]

    binary_img_data = img_data.decode('base64')

    file_like = BytesIO(binary_img_data)

    return Image.open(file_like)

def paint_background(img):
    img.save('raw.png')

    # 'L' - 转换成8bits黑白图片
    gray = img.convert('L')
    gray.save('gray.png')

    # 仅在源图片为 L(8bits像素黑白图片) 或 P(8bits像素调色板图片) 时，才可输出 1(1-bit像素黑白图片)
    bw = gray.point(lambda x: 0 if x < 1 else 255, '1')
    bw.save('modified.png')

    return bw

def img2string(img):
    #Prerequisites:
    # - Python-tesseract requires python 2.5+ or python 3.x
    # - You will need the Python Imaging Library (PIL) (or the Pillow fork).
    # Under Debian/Ubuntu, this is the package **python-imaging** or **python3-imaging**.
    # - Install `Google Tesseract OCR <https://github.com/tesseract-ocr/tesseract>`_
    # (additional info how to install the engine on Linux, Mac OSX and Windows).
    # You must be able to invoke the tesseract command as *tesseract*.
    # If this isn't the case, for example because tesseract isn't in your PATH,
    # you will have to change the "tesseract_cmd" variable ``pytesseract.pytesseract.tesseract_cmd``.
    # Under Debian/Ubuntu you can use the package **tesseract-ocr**.
    # For Mac OS users. please install homebrew package **tesseract**.
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
    tessdata_dir_config = '--tessdata-dir "C:/Program Files (x86)/Tesseract-OCR"'
    word = pytesseract.image_to_string(img, config=tessdata_dir_config, lang="eng")
    return ''.join(c for c in word if c in string.letters).lower()

def register(reg_url, first_name, last_name, email, password, password_two):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(reg_url).read()

    form = parse_form(html)
    form['first_name'] = first_name
    form['last_name'] = last_name
    form['email'] = email
    form['password'] = password
    form['password_two'] = password_two
    form['recaptcha_response_field'] = img2string(paint_background(get_captcha(html)))

    print form['recaptcha_response_field']

    encoded_data = urllib.urlencode(form)

    request = urllib2.Request(reg_url, encoded_data)

    response = opener.open(request)

    print response.geturl()
    return response.geturl()

if __name__ == '__main__':
    # main('http://example.webscraping.com/places/default/user/login',
    #      'example@webscraping.com',
    #      'example')
    # mechanize_form('http://example.webscraping.com/places/default/user/login',
    #                'example@webscraping.com',
    #                'example')
    str = register('http://example.webscraping.com/places/default/user/register',
                   'wn',
                   'wzhnsc',
                   'wzhnsc@163.com',
                   '123456',
                   '123456')
    print '/user/register' not in str