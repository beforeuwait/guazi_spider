# coding=utf8

"""
    auther  : wangjiawei
    date    : 2018-08-28

    - schedule:
    08-28:  开始开发
    08-30:  添加seedsMangement
    08-31:  开始添加redis模块，引入消息队列

    09-03:  弱化schedule，只是负责调度，监督各个节点的状态，体力活交给slave去做
    09-04:  之前的设计都推翻,schedule承担的角色为:协调资源
    09-05:  开始写schedule
        1. 先设置一个节点为session管理
        2. 再设置一个节点seed管理
        3. 再设置一个节点为persistence管理
        4. 该schedule完成使命
"""

import time
import os
import config
from config import redis_cli
from config import logger
from utils import loads_json
from utils import dumps_json
from utils import wait_for_msg


def guazi_platform():
    """瓜子抓取系统的调度"""

    print('系统启动顺序\n\t1.SessionMangement\n\t2.SeedMangement\n\t3.PersistenceMangement')
    # 第一个启动session管理
    start_node_in_order('ssnm')

    # 第二个启动seed管理
    start_node_in_order('sedm')

    # 第三个启动psm管理
    start_node_in_order('psm')

def start_node_in_order(cmd):
    """
    将指定的命令放入队里
    """
    que = config.task_que
    order = {
        'ssnm': {'cmd': {'command': 'ssnm'}, 'name': 'SessionMangement'},
        'sedm': {'cmd': {'command': 'sedm'}, 'name': 'SeedMangement'},
        'psm': {'cmd': {'command': 'psm'}, 'name': 'PersistenceMangement'}
    }
    print('启动\t{0}'.format(order.get(cmd).get('name')))
    redis_cli.lpush(que, dumps_json(order.get(cmd).get('cmd')))
    # 等待回馈
    wait_feed_back()
    print('完成启动')
    return


def wait_feed_back():
    """用于启动顺序中获取子节点的反馈"""
    que = config.task_que_fb
    while True:
        if redis_cli.exists(que):
            # 说明有反馈了，把该条数据拿出来
            redis_cli.rpop(que)
            break
        time.sleep(0.1)


if __name__ == '__main__':
    guazi_platform()