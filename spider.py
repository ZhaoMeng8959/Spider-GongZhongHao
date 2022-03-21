#!/usr/bin/env python
# --*-- coding:UTF-8 --*--

import os
import re
import json
import time
import random
import shutil
import pymysql
import requests
import datetime
from threading import Thread
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from pymysql.converters import escape_string

sess = requests.Session()
# max_retries=10 重试10次
sess.mount('http://', HTTPAdapter(max_retries=10))
sess.mount('https://', HTTPAdapter(max_retries=10))

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

file_save_path = file_path + r'/spider/'

if CONFIG['save_to_mysql']:
    mysql_conn = CONFIG['mysql_connect']
    conn = pymysql.connect(host=mysql_conn['ip_address'],
                           port=mysql_conn['port_number'],
                           user=mysql_conn['username'],
                           passwd=mysql_conn['password'],
                           db=mysql_conn['db_name'],
                           autocommit=True,
                           charset='utf8mb4')

# 全局参数
cur_spider_pattern = 0
cur_cookie_number = 0
cur_official_account_name = None
cur_serial_number = 0
latest_url = None


def start():
    while True:
        for official_account_name in CONFIG.get('official_accounts_name'):
            global cur_spider_pattern, cur_cookie_number, cur_official_account_name, cur_serial_number, latest_url

            cur_spider_pattern = CONFIG['spider_pattern']
            cur_official_account_name = official_account_name
            cur_serial_number = CONFIG['cur_serial_number'][cur_official_account_name]

            print('----- 当前爬取模式：%d -----' % CONFIG['spider_pattern'])

            # 获取上次爬取最新的文章，如果配置为：仅抓取未抓取的文章，则会在爬取过程中使用该参数进行判断
            # 若采用模式1爬取，默认开始爬取序号都为0
            if cur_spider_pattern == 1:
                cur_serial_number = 0
                latest_url = get_latest_article_from_mysql()

            while True:
                print('----- 当前cookie序号: %d -----' % cur_cookie_number)

                # 初始化请求参数
                init_param()

                print('----- 开始查询公众号[%s]相关文章 -----' % official_account_name)
                response = requests.get(weixin_search_url,
                                        cookies=CONFIG['cookies'][cur_cookie_number],
                                        headers=headers,
                                        params=REQUEST_PARAM_2, timeout=10)
                time.sleep(10)

                # 获取文章总数
                total_num = response.json().get('app_msg_cnt')

                if total_num is None:  # cookie失效或者被封
                    print('----- 查询失败！请确认公众号名或该查询账号被禁止使用 -----')
                    print('----- 开始切换公众号 -----')
                    break
                elif total_num == 0:  # 查询公众号未发表文章
                    print('----- 查询成功! 文章总数：%s' % str(total_num))
                    print('----- 开始切换公众号 -----')
                    break
                else:
                    print('----- 查询成功! 文章总数：%s' % str(total_num))
                    cur_serial_number = get_article(total_num)

                    # 当文章爬取结束，切换公众号爬取
                    if cur_serial_number >= total_num:
                        # 将config.json文件中对应的起始爬取数设置为0
                        if cur_spider_pattern == 0:
                            cur_serial_number = 0
                            save_cur_serial_number_to_config()

                        cur_cookie_number += 1
                        cur_cookie_number %= len(CONFIG['cookies'])
                        print('----- 开始切换公众号 -----')
                        break;

                cur_cookie_number += 1
                cur_cookie_number %= len(CONFIG['cookies'])
            print('----- 公众号[%s]文章爬取结束！ -----' % official_account_name)
            print('----- 开始切换公众号 -----')


def get_latest_article_from_mysql():
    un_id = CONFIG['un_id'][cur_official_account_name]
    mysql_cur = conn.cursor()
    sql = 'SELECT url FROM `spider_gongzhonghao_result` WHERE un_id = %d order by `chrono` DESC LIMIT 1;' % un_id
    mysql_cur.execute(sql)
    select_result = mysql_cur.fetchone()
    if select_result is None:
        return None
    return select_result[0]


# 为防止程序意外中止导致爬取不全，将爬取文章的序号保存到config.json中，每次请求都从配置文件中初始化
def save_cur_serial_number_to_config():
    CONFIG['cur_serial_number'][cur_official_account_name] = cur_serial_number
    save_file = file_path + '/config.json'
    with open(save_file, 'w', encoding='UTF-8') as file:
        file.truncate()
        file.write(json.dumps(CONFIG, ensure_ascii=False))
        file.close()


def init_param():
    response = requests.get(url=weixin_url_before_login, cookies=CONFIG['cookies'][cur_cookie_number], timeout=10)
    token = re.findall(r'token=(\d+)', str(response.url))[0]
    time.sleep(2)
    REQUEST_PARAM_1['token'] = token
    REQUEST_PARAM_1['query'] = cur_official_account_name
    print('----- 正在查询[%s]相关公众号 -----' % cur_official_account_name)
    response = requests.get(weixin_url_after_login, cookies=CONFIG['cookies'][cur_cookie_number], headers=headers,
                            params=REQUEST_PARAM_1, timeout=10)
    # 解决: 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败
    if response is None:
        time.sleep(10 * 60)
        return
    time.sleep(2)
    print('----- 查询成功，默认选择返回结果的第一条数据 -----')
    lists = response.json().get('list')[0]
    REQUEST_PARAM_2['token'] = token
    REQUEST_PARAM_2['fakeid'] = lists.get('fakeid')
    REQUEST_PARAM_2['nickname'] = lists.get('nickname')


def get_article(total_num):
    current_num = cur_serial_number
    while current_num < total_num:
        REQUEST_PARAM_2['begin'] = current_num
        REQUEST_PARAM_2['random'] = random.random()
        response = requests.get(weixin_search_url, cookies=CONFIG['cookies'][cur_cookie_number], headers=headers,
                                params=REQUEST_PARAM_2, timeout=10)
        print('----- 开始爬取第%d条到%d条文章 -----' % (
            current_num + 1, current_num + len(response.json().get('app_msg_list', []))))
        time.sleep(5)
        count = 1
        for per in response.json().get('app_msg_list', []):
            # 已经获取上次爬取最新的文章，且配置为：仅抓取未抓取的文章，则直接退出
            if CONFIG['spider_pattern'] == 1 and per.get('link') == latest_url:
                return total_num

            print('----- 开始下载第%d篇文章 -----' % (current_num + count))

            # 初始化要保存的参数
            aid = per.get('aid')
            title = re.sub(r'[\|\/\<\>\:\*\?\\\"]', "_", per.get('title'))
            digest = per.get('digest')
            link = per.get('link')
            create_time = per.get('create_time')
            update_time = per.get('update_time')

            # 保存到文件中
            if CONFIG['save_to_file']:
                filepath = file_save_path + cur_official_account_name + '/' + str(per.get('create_time')) + '_' + title
                if save_article_to_file(filepath, title, link):
                    print('----- 文件: 第%d篇文章下载成功 -----' % (current_num + count))

            # 保存到数据库中
            if CONFIG['save_to_mysql']:
                if save_article_to_mysql(title, link, create_time, update_time):
                    print('----- 数据库: 第%d篇文章下载成功 -----' % (current_num + count))

            count += 1
            time.sleep(random.randint(1, 5))

        current_num += len(response.json().get('app_msg_list', []))

        # 开启一个新的线程，用来执行config.json文件修改保存的操作
        if cur_spider_pattern == 0:
            save_config_thread = Thread(target=save_cur_serial_number_to_config,
                                        args=(cur_official_account_name, current_num,))
            save_config_thread.start()

        # 爬取文章数超过30篇就更换cookie
        if current_num - cur_serial_number >= 30:
            return current_num

        # 睡眠30秒到60秒，防止被封
        time.sleep(random.randint(30, 60))
    return total_num


def save_article_to_file(filepath, title, link):
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
    os.makedirs(filepath)
    os.chdir(filepath)
    html = sess.get(link, headers=headers, timeout=10)
    soup_html = BeautifulSoup(html.text, 'lxml')
    article = soup_html.find('div', id='js_content')

    # Case 1: 文章内容涉嫌违反法律法规和政策导致发送失败
    if article is None:
        print('----- 保存失败：文章内容涉嫌违反法律法规和政策导致发送失败 -----')
        return False

    # 保存文章到本地
    file_name = title + '.txt'
    with open(file_name, 'a+', encoding='UTF-8') as file:
        file.truncate()
        file.write(article.text)
        file.close()

    # 保存图片到本地
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
            log_file_path = file_save_path + 'log/' + cur_official_account_name + '/'
            if not os.path.exists(log_file_path):
                os.makedirs(log_file_path)
            os.chdir(log_file_path)
            with open(file_name, 'a+', encoding='UTF-8') as file:
                file.write(link)
                file.write('\n')
                file.close()
    return True


def save_article_to_mysql(title, link, create_time, update_time):
    html = sess.get(link, headers=headers, timeout=10)
    soup_html = BeautifulSoup(html.text, 'lxml')
    article = soup_html.find('div', id='js_content')

    # Case 1: 文章内容涉嫌违反法律法规和政策导致发送失败
    if article is None:
        print('----- 保存失败：文章内容涉嫌违反法律法规和政策导致发送失败 -----')
        return False

    link = escape_string(link)
    title = escape_string(title)
    article = escape_string(article.text)

    # 时间戳->指定日期格式
    time_format_str = '%Y-%m-%d %H:%M:%S'
    update_time = time.strftime(time_format_str, time.localtime(update_time))
    now = datetime.datetime.now().strftime(time_format_str)

    # 从数据库查询即将插入的数据，判断是更新还是新增
    mysql_cur = conn.cursor()
    sql = 'SELECT last_update_time FROM `spider_gongzhonghao_result` WHERE url = "%s";' % link
    mysql_cur.execute(sql)
    select_result = mysql_cur.fetchone()

    # 更新
    if not select_result is None:
        up_time = time.mktime(time.strptime(str(update_time), time_format_str))
        mysql_up_time = time.mktime(time.strptime(str(select_result[0]), time_format_str))
        if int(up_time) != int(mysql_up_time):
            sql = '''UPDATE `spider_gongzhonghao_result` 
	    			 SET `un_id`=%d, `url`="%s", `title`="%s", `content`="%s" , 
	    			     `chrono`=%d, `type`=%d, `count`=%d, `last_scan_time`="%s", `last_update_time`="%s"
	    			 WHERE url = "%s";''' \
                  % (
                      CONFIG['un_id'][cur_official_account_name], link, title, article, create_time, 0, 0, now,
                      update_time, link)
            mysql_cur.execute(sql)
    # 新增
    else:
        sql = '''INSERT INTO `spider_gongzhonghao_result` 
                 (`un_id`, `url`, `title`, `content`, `chrono`, `type`, `count`, `last_scan_time`, `last_update_time`) 
                 VALUES (%d, "%s", "%s", "%s", %d, %d, %d, "%s", "%s");''' \
              % (
                  CONFIG['un_id'][cur_official_account_name], link, title, article, create_time, 0, 0, now,
                  update_time)
        mysql_cur.execute(sql)
    mysql_cur.close()
    return True


if __name__ == '__main__':
    print('----- Spider_GongZhongHao -----')
    start()
