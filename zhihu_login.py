# -*- coding:utf-8 -*-
import os
import time
import json
import requests
from bs4 import BeautifulSoup

session = requests.session()


def kill_captcha(data):
    img_name = 'D:/captcha.png'
    with open(img_name, 'wb') as fp:
        fp.write(data)
    os.system("%s" % img_name)
    return raw_input('captcha : ')


def save_cookies(session):
    with open("D:/cookiefile.txt", 'w') as f:
        json.dump(session.cookies.get_dict(), f)


def read_cookies():
    with open('D:/cookiefile.txt') as f:
        cookie = json.load(f)
        session.cookies.update(cookie)
        return session


def login(username, password, oncaptcha):
    _xsrf = BeautifulSoup(session.get('https://www.zhihu.com/#signin').content, "lxml").find('input', attrs={'name': '_xsrf'})['value']
    captcha_content = session.get('http://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000)).content
    data = {
        '_xsrf': _xsrf,
        'email': username,
        'password': password,
        'remember_me': 'true',
        'captcha': oncaptcha(captcha_content)
    }

    header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36',
            'Host': 'www.zhihu.com',
            'Referer': 'www.zhihu.com'
            }

    resp = session.post('http://www.zhihu.com/login/email', data=data, headers=header).content
    if '\u767b\u9646\u6210\u529f' in resp:
        name = BeautifulSoup(session.get("https://www.zhihu.com").content, "lxml").find('span', class_='name').getText()
        print u'%s登陆成功! 开始准备爬取数据 \(^o^)/YES!' % name
        save_cookies(session)
    else:
        print u'您的账号密码可能输入错误，还请再检查下验证码。'
    return session


