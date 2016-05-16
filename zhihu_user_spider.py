# -*- coding: utf-8 -*-

"""
@author: Ningersan
@email: Ningersan@outlook.com
"""

import os
import re
import socket
import zhihu_login
from os.path import basename
from urlparse import urlsplit
from bs4 import BeautifulSoup


class Tool:
    remove_img = re.compile('<img.*?>')
    remove_addr = re.compile('<a.*?>|</a>')
    replace_br = re.compile('<br>')
    replace_b = re.compile('<b>|</b>')
    replace_i = re.compile('<i.*?>|</i>')
    replace_p = re.compile('<p>|</p>')
    replace_c = re.compile('\?|\*|\"|:|<|>|/')

    def replace_text(self, x):
        x = re.sub(self.remove_img, '', x)
        x = re.sub(self.remove_addr, '', x)
        x = re.sub(self.replace_br, '\n', x)
        x = re.sub(self.replace_b, '', x)
        x = re.sub(self.replace_i, '', x)
        x = re.sub(self.replace_p, '', x)
        return x.strip()

    def replace_title(self, x):
        x = re.sub(self.replace_c, '', x)
        return x.strip()


class ZHAS:
    def __init__(self, name):
        self.author = name
        self.page_num = 1
        self.tool = Tool()
        self.base_url = 'https://www.zhihu.com'
        self.url = 'https://www.zhihu.com/people/%s/answers?' % name
        self.base_url = 'https://www.zhihu.com'
        self.soup = None
        self._session = self.login()

    def login(self):
        if os.path.exists('D:/cookiefile.txt'):
            return zhihu_login.read_cookies()
        else:
            username = raw_input(u'请输入您的邮箱账号：')
            password = raw_input(u'请输入您的密码：')
            return zhihu_login.login(username, password, zhihu_login.kill_captcha)

    def mk_dir(self, author, title):
            path = 'D:/answers/' + u'%s' % author + '/' + u'%s' % title
            if not os.path.exists(path):
                os.makedirs(path)
                print u'已创建%s文件夹' % path
            else:
                print u'文件夹%s已存在' % path
            return path

    def parse_html(self, url):
        resp = self._session.get(url)
        if resp.status_code == 200:
            self.soup = BeautifulSoup(resp.content, 'html.parser')
        else:
            print 'you may enter the wrong id 0.0, please check it out '
            resp.raise_for_status()

    def get_answer_num(self):
        answer_num = int(self.soup.find('a', class_='item active').find('span', class_='num').string)
        print u'一共回答了%d个问题。' % answer_num
        return answer_num

    def get_author_info(self):
        soup = self.soup
        author = soup.find('a', class_='name').string
        follow_soup = soup.find('div', class_='zm-profile-side-following zg-clear').find_all('a', class_='item')
        followees = follow_soup[0].find('strong').string
        followers = follow_soup[1].find('strong').string
        title = soup.find('span', class_='bio').string
        description = soup.find('span', class_='content')
        print u'您输入的是%s的主页' % author
        print u'%s' % title
        if description:
            print u'%s' % description.getText().strip()
        else:
            print 'None'
        print u'TA 关注了%s个人  有%s个粉丝。' % (followees, followers)
        raw_input(u'输入任意键开始爬取数据：')
        return author

    def get_content(self, url, author):
        self.parse_html(url)
        soup = self.soup
        answers_soup = soup.find_all('div', class_='zm-item')

        for answer_soup in answers_soup:
            title = answer_soup.find('a', class_='question_link').getText()
            vote = answer_soup.find('div', class_='zm-item-vote').find('a').getText()
            if answer_soup.find('div', class_='answer-status'):
                content = answer_soup.find('div', class_='answer-status').find('p').getText()
                answer_url = self.base_url + answer_soup.find('a', class_='question_link').get('href')
            else:
                content = answer_soup.find('textarea').getText()
                answer_url = self.base_url + answer_soup.find('p', class_='visible-expanded').find('a').get('href')
            file_title = self.tool.replace_title(title)
            text = self.tool.replace_text(content)
            print u'正在写入文件中......'
            with open(self.mk_dir(author, file_title) + '/%s.txt' % file_title, 'w+') as fp:
                fp.write('\n------------' + '%s' % title.encode('utf-8') + '------------\n')
                fp.write('\n------------' + u'赞同数  '.encode('utf-8') + str(vote) + '------------\n\n')
                fp.write(text.encode('utf-8'))
                fp.write('\n\n\n' + u'详细请见    '.encode('utf-8') + str(answer_url))

            img_urls = BeautifulSoup(content, "lxml").find_all('img')
            for detail in img_urls:
                img_url = detail.get('src')
                file_name = basename(urlsplit(img_url)[2])
                file_path = 'D:/answers/' + u'%s' % author + '/' + u'%s' % file_title
                try:
                    img_data = self._session.get(img_url).content
                    print u'正在下载 %s' % img_url
                    with open(file_path + '/' + file_name, 'wb') as fp:
                        fp.write(img_data)
                except:
                    print u'对不起，%s下载失败。' % img_url

    def start(self):
        self.parse_html(self.url)
        author = self.get_author_info()
        limits = (self.get_answer_num() - 1) / 20 + 1
        while self.page_num <= limits:
            self.get_content(self.url + 'page=%d' % self.page_num, author)
            self.page_num += 1
        print 'Done !!!'

author_id = raw_input(u'请输入作者的id：')
socket.setdefaulttimeout(5.0)
run = ZHAS(author_id)
run.start()

