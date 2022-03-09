#!/usr/bin/env python
# --*-- coding:UTF-8 --*--

import json
import os
import re
import time
import random
import requests
from bs4 import BeautifulSoup

sess = requests.Session()

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, 'config.json'), encoding='UTF-8') as fp:
    CONFIG = json.load(fp)

weixin_url_before_login = "https://mp.weixin.qq.com/"

weixin_url_after_login = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'

weixin_search_url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?'

headers = {
    'HOST': 'mp.weixin.qq.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/72.0.3626.109 Safari/537.36 '
}

file_save_path = file_path + r'/spider/'

REQUEST_PARAM_1 = {
    'action': 'search_biz',
    'token': '',
    'random': random.random(),
    'query': '',
    'lang': 'zh_CN',
    'f': 'json',
    'ajax': '1',
    'begin': '0',
    'count': '5'
}

REQUEST_PARAM_2 = {
    'action': 'list_ex',
    'token': None,
    'random': random.random(),
    'fakeid': None,
    'lang': 'zh_CN',
    'f': 'json',
    'ajax': '1',
    'begin': 0,
    'count': 5,
    'query': '',
    'type': '9'
}


def start():
    for official_account_name in CONFIG['official_accounts_name']:
        init_param(official_account_name)
        print('----- 开始查询公众号[%s]相关文章 -----' % official_account_name)
        response = requests.get(weixin_search_url, cookies=CONFIG['cookies'], headers=headers, params=REQUEST_PARAM_2)
        time.sleep(2)
        print('----- 查询成功! -----')
        total_num = response.json().get('app_msg_cnt')
        print('----- 文章总数：' + str(total_num))
        get_article(official_account_name, total_num)


def init_param(official_account_name):
    response = requests.get(url=weixin_url_before_login, cookies=CONFIG['cookies'])
    token = re.findall(r'token=(\d+)', str(response.url))[0]
    time.sleep(2)
    REQUEST_PARAM_1['token'] = token
    REQUEST_PARAM_1['query'] = official_account_name
    print('----- 正在查询[%s]相关公众号 -----' % official_account_name)
    response = requests.get(weixin_url_after_login, cookies=CONFIG['cookies'], headers=headers, params=REQUEST_PARAM_1)
    time.sleep(2)
    print('----- 查询成功，默认选择返回结果的第一条数据 -----')
    lists = response.json().get('list')[0]
    REQUEST_PARAM_2['token'] = token
    REQUEST_PARAM_2['fakeid'] = lists.get('fakeid')
    REQUEST_PARAM_2['nickname'] = lists.get('nickname')


def get_article(official_account_name, total_num):
    current_num = 0
    while current_num <= total_num:
        REQUEST_PARAM_2['begin'] = current_num
        REQUEST_PARAM_2['random'] = random.random()
        response = requests.get(weixin_search_url, cookies=CONFIG['cookies'], headers=headers, params=REQUEST_PARAM_2)
        print('----- 开始爬取第%d条到%d条文章 -----' % (
            current_num + 1, current_num + len(response.json().get('app_msg_list', []))))
        time.sleep(5)
        count = 1
        for per in response.json().get('app_msg_list', []):
            print('----- 开始下载第%s篇文章 -----' % str(current_num + count))
            title = re.sub(r'[\|\/\<\>\:\*\?\\\"]', "_", per.get('title'))
            link = per.get('link')
            filepath = file_save_path + official_account_name + '/' + str(per.get('create_time')) + '_' + title
            save_article(filepath, title, link)
            print('----- 第%s篇文章下载成功 -----' % str(current_num + count))
            count += 1
        current_num += len(response.json().get('app_msg_list', []))


def save_article(filepath, title, link):
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    os.chdir(filepath)
    html = sess.get(link, headers=headers)
    soup_html = BeautifulSoup(html.text, 'lxml')
    article = soup_html.find('div', id='js_content').text
    file_name = title + '.txt'
    with open(file_name, 'a+', encoding='UTF-8') as file:
        file.write(article)
        file.close()
    img_urls = soup_html.find('div', id='js_content').find_all("img")
    for i in range(len(img_urls)):
        try:
            if img_urls[i]['data-src']:
                img_url = img_urls[i]['data-src']
            else:
                img_url = img_urls[i]["src"]
            pic_down = requests.get(img_url)
            with open(str(i) + r'.jpeg', 'ab+') as file:
                file.write(pic_down.content)
                file.close()
        except KeyError:
            log_file_path = file_save_path + 'log.txt'
            if not os.path.exists(log_file_path):
                os.makedirs(log_file_path)
            os.chdir(log_file_path)
            with open(file_name, 'a+', encoding='UTF-8') as file:
                file.write(link)
                file.write('\n')
                file.close()


if __name__ == '__main__':
    print('----- Spider_公众号 -----')
    start()
