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
        re = redis.StrictRedis(host=host, port=port, db=1)
    except Exception as e:
        logger.warning('请启动\tredis\t服务, {0}'.format(e))
    return re

redis_cli = connect_redis()

#   消息队列名称

task_que = 'TaskQue'

# session请求队列
ssn_req = 'ssnreq'

# session回复队列
ssn_rep = 'ssnrep'

# session状态队列
ssn_status = 'ssnsts'

# seed请求队列
sed_req = 'sedreq'

"""
task_que_fb = 'TaskQueueFB'

cookie_que = 'CookieQue'

ssn_sed_que = 'CookieQue1'

sed_ssn_que = 'CookieQue2'

feedback_que = 'FeedbackQue'
"""


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
