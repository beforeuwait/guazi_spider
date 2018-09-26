# coding=utf8

"""
    author  : wangjiawei
    date    : 2018-08-28

    - 作为slaver部分，一次启动 x个子进程，每个子进程嗷嗷待哺
    - 管理子进程, 通过 supervisor ?

    # 09-03:    赋予slave更多的功能
        1. 汇报状态, cpu状态, 内存状态, 主动的方式用一条反向队列
        2. 负责构造种子，派发种子
        3. 暂时只想了这么多

    # 09-04:    说说slave 的思路

    slave的功能:
        1. 变成SessionMangement 节点，负责session管理
        2. 变成SeedsMangement 节点，负责seed管理
        3. 变成PersistenceMangement 节点，负责持久化管理
        4. 接收普通请求任务，完成请求
            . 需要同session管理节点通信

    # todo: 如何来确定每个节点的编号

"""

import time
import config
import random
import datetime
from config import redis_cli
from SessionMangement import SessionMangement
from SeedsMangement import SeedsMangement
from PersistenceMangement import listn_the_psm_que
from SpiderHandler import SpiderHandler
from utils import loads_json


def listen_task_que():
    """启动后
    开始监听 Task_Que
    拿到任务，先弄清是是个啥
    在转换自己的角色

    正常的种子 {"url": "xxxx", ......}
    任务: {"command": "xxxx"}
        session管理: ssnm
        seed管理: sedm
        persistence管理: psm

    # 09-07更新。需要为每一个节点打上一个标记
        为了不放js文件混乱，才这样的。

    """
    task_que = config.task_que
    mark_que = config.mark_que
    # 在监听任务前，需要先监听mark_que
    # 具体就是，从mark队列里拿到数字标号
    # 自增1作为自己的标号
    # 同时将自己的标号放入mark队列里

    # 先监听mark队列，拿到自己的编号
    while True:
        if redis_cli.exists(mark_que):
            msg = redis_cli.rpop(mark_que)
            if not msg:
                continue
            mark = int(msg.decode()) + 1
            break
        time.sleep(random.random())
    # 放入队列里
    redis_cli.lpush(mark_que, mark)
    print('当前slave编号\t{0}'.format(mark))
    # 完成了后，才开始监听这个任务队列

    while True:
        if redis_cli.exists(task_que):
            msg = redis_cli.rpop(task_que)
            # 开始分类msg属于什么任务:
            #
            if not msg:
                continue
            msg_dict = loads_json(msg.decode())
            print('{0}\t收到数据'.format(datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')))
            # 开始分类:
            if msg_dict.get('command'):
                # 这里commend
                commend = msg_dict.get('command')
                if commend == 'ssnm':
                    sm = SessionMangement()
                    sm.session_main_logic()
                elif commend == 'sedm':
                    sm = SeedsMangement()
                    sm.seed_main_logic()
                else:
                    # 化身持久化模块
                    listn_the_psm_que()

            else:
                # 那就是种子了
                # 这里要做的事情有
                # 1. 请求一个cookie
                # 2. 完成html的请求
                # 3. data放入psm队列里
                # 4. 反馈给seesion/seed模块
                time.sleep(random.random()*20)
                seed = msg_dict
                # 调度spider, 把mark放入实例化中
                sp = SpiderHandler(mark)
                sp.receive_seed_and_start_crawl(seed)
                # 结束上一个，等下一个种子
                del sp

        time.sleep(0.1)


if __name__ == '__main__':
    listen_task_que()