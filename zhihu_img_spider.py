# !/usr/bin/python
# -*- coding:utf-8 -*-

"""
@author: Ningersan
@email: Ningersan@outlook.com
"""

import re
import os
import json
import socket
import urllib
import requests


class ZHSP:
    def __init__(self):
        self.img_num = 0
        self.failures = 0
        self.offset = 0
        self.page_size = 20
        self.base_url = 'https://www.zhihu.com/question/'
        self.ques_num = raw_input(u'请输入完整的网址 https://www.zhihu.com/question/: ')
        self.url = self.base_url + str(self.ques_num)
        self.post_url = 'http://www.zhihu.com/node/QuestionAnswerListV2'
        self.header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36',
                'Host': 'www.zhihu.com',
                'Referer': self.url
                }

    def mk_dir(self, name):
        path = 'D:\\image\\' + u'%s' % self.get_title(self.url) + '\\' + u'%s' % name
        if not os.path.exists(path):
            os.makedirs(path)
            print u'已创建%s文件夹' % path
        return path

    def cut_url(self, url):
        i = -1
        while url[i] != '/':
            i -= 1
        return url[i:]

    def answer_num(self, url):
        html = requests.get(url, headers=self.header).content
        pattern = re.compile('<h3 data-num="(.*?)"')
        num = re.search(pattern, html)
        print u'发现了%d个答案哟~' % int(num.group(1))
        return int(num.group(1))

    def get_title(self, url):
        html = requests.get(url, headers=self.header).content
        pattern = re.compile("<title>(.*?)</title>", re.S)
        title = re.search(pattern, html)
        return title.group(1).strip().decode('utf-8')

    def get_page(self, url):
        data = {
            'method': 'next',
            'params': json.dumps({
                'url_token': int(self.ques_num),
                'pagesize': self.page_size,
                'offset': self.offset
            }),
            '_xsrf': ''
        }
        try:
            return requests.post(url, data=data, headers=self.header).content
        except:
            print 'sorry, we can not get the html...'

    def download_img(self, html):
        pattern = re.compile('img .*?data-actualsrc="(.*?_b.*?)"')
        answer_list = json.loads(html)['msg']
        for i in range(0, len(answer_list)):
            author = re.search(re.compile('.*?data-author-name="(.*?)".*?'), answer_list[i]).group(1)
            img_urls = re.findall(pattern, answer_list[i])
            if img_urls:
                print u'%s 有 %s 张图片.' % (author, len(img_urls))
                for img_url in img_urls:
                    img_original = img_url.replace('_b', '_r')
                    file_name = self.mk_dir(author) + self.cut_url(img_original)
                    try:
                        urllib.urlretrieve(img_original, file_name)
                        print u'正在下载 %s 中' % img_original
                        self.img_num += 1
                    except:
                        print u'很不幸，下载 %s 失败了 ╮(╯▽╰)╭' % img_original
                        self.failures += 1
            else:
                print u'%s 并没有图片 ┑(￣Д ￣)┍' % author
            print '\n'

    def start(self):
        limits = self.answer_num(self.url)
        while self.offset < limits:
            html = self.get_page(self.post_url)
            self.download_img(html)
            self.offset += self.page_size
        print u'一共下载了%s张图片哦' % self.img_num
        print u'失败了%s张图哦' % self.failures

socket.setdefaulttimeout(10.0)

run = ZHSP()
run.start()
