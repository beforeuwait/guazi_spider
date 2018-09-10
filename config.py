# coding=utf8

import os
import redis

os.chdir(os.path.split(os.path.abspath(__file__))[0])

import logging
# 日志部分

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('logging.log')
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

#   redis模块
#   在导入config之处，就已经实例化并链接了redis了

host = 'localhost'
port = 6379
db = 1

def connect_redis():
    """链接到redis"""
    re = None
    try:
        re = redis.StrictRedis(host=host, port=port, db=3)
    except Exception as e:
        logger.warning('请启动\tredis\t服务, {0}'.format(e))
    return re

redis_cli = connect_redis()

#   消息队列名称

# mark_que

mark_que = 'mark'

task_que = 'TaskQue'

task_que_fb = 'TaskQueFb'

# session请求队列
ssn_req = 'ssnreq'

# session回复队列
ssn_rep = 'ssnrep'

# session状态队列
ssn_status = 'ssnsts'

# seed请求队列
sed_req = 'sedreq'

# 持久化队列
psm_que = 'psmque'


# 消息队列引用



#   [LoginHander.py]

home_page_url = "http://www.guazi.com"

log_in_xpath = {
    'adv2': '/html/body/div[2]/div[2]/div/div/div[2]/a[1]',
    'log_btn': '//*[@id="js-login"]',
    'phone_number': '/html/body/div[3]/div[2]/form/ul/li[1]/input',
    'captcha_btn': '/html/body/div[3]/div[2]/form/ul/li[2]/button',
    'captcha_input': '/html/body/div[3]/div[2]/form/ul/li[2]/input',
    'commit_btn': '/html/body/div[3]/div[2]/form/button',
}

user_info_file = './DB/user_info.txt'

#   种子部分

offset_file = './DB/seed_offset.txt'

seeds_store = './DB/seeds_store.txt'

#   [spiderHandler]

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Host": "www.guazi.com",
    "Referer": "https://www.guazi.com",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}

ua_list = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        ]

request_retry = 2

#   [持久化部分]

data_file = './DB/guazi_data.txt'

token = './DB/guazi_token.txt'

hdfs_path = '/user/spider/car_price/guazi/guazi_data.txt'

hdfs_ip = '47.98.32.168:50070'

user_name = 'spider'

