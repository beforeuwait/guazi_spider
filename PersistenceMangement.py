# coding=utf8

"""
    author: wangjiawei
    date:   2018-09-05

    该模块主要作为持久化模块
    监听 ps_que队列
    获取数据，然后持久化操作

"""


import time
import config
import datetime
from config import logger
from config import redis_cli
from utils import translate_2_json_dict
from utils import loads_json
from utils import write_2_file
from utils import make_set
from utils import dumps_json
from pyhdfs import HdfsClient

# 持久化队列
psm_que = config.slv_2_psm

data_file = config.data_file

hdfs_path = config.hdfs_path

token = config.token

def listn_the_psm_que():
    """持续监听psm_que这个队列
    只要一有数据过来，就做存储
    """
    # 先反馈
    # 完成后像队里推送一条已完成启动
    print('持久化队列启动')
    que = config.task_que_fb
    ctx = dumps_json({'psm': 'done'})
    redis_cli.lpush(que, ctx)
    while True:
        if redis_cli.exists(psm_que):
            # 就开始处理
            token_set = make_set(token, blank='', index='')
            msg = redis_cli.rpop(psm_que)
            seed = loads_json(translate_2_json_dict(msg))
            print('{0}\t收到数据'.format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
            # 接下来就是做持久化处理了
            do_persistence(seed, token_set)
        time.sleep(0.1)


def do_persistence(seed, id_set):
    """
    做持久化处理
    :param seed:待持久化的文件
    """

    data_list = seed.get('data')
    for each in data_list:
        if each[0] not in id_set:
            ctx = []
            # 首先构建字段
            ctx.append(seed.get('brand_id'))
            ctx.append(seed.get('brand'))
            ctx.append(seed.get('serise_id'))
            ctx.append(seed.get('serise'))
            ctx.append(seed.get('p_type'))
            ctx.extend(each)
            ctx.append(seed.get('date'))
            ctx.append(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
            ctx.append(str(seed.get('epoh')))
            # 写入数据
            text = '\u0001'.join(ctx)
            write_2_file(data_file, text)
            # 写入hdfs
            append_2_hdfs(text)
            # 记录new token
            write_2_file(token, each[0])
            del ctx
        else:
            print('数据id已存在')


def connect_hdfs():
    return HdfsClient(hosts='47.98.32.168:50070', user_name='spider')

def append_2_hdfs(text):

    try:
        hdfs = connect_hdfs()
        # 先看看文件在不在
        if not hdfs.exists(hdfs_path):
            hdfs.create(hdfs_path, (text + '\n').encode())
        else:
            hdfs.append(hdfs_path, (text + '\n').encode())
        logger.info('完成写入集群....')
    except:
        logger.warning('集群写入错误')
