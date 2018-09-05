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
from config import redis_cli
from SessionMangement import SessionMangement
from SeedsMangement import SeedsMangement
from PersistenceMangement import PersistenceMangement
from utils import translate_2_json_dict
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

    引入sub广播

    """
    que = config.task_que

    while True:
        if redis_cli.exists(que):
            msg = redis_cli.rpop(que)
            # 开始分类msg属于什么任务:
            #
            msg_dict = loads_json(translate_2_json_dict(msg))
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
                    psm = PersistenceMangement()
                    # todo: 添加主要方法
            else:
                # 那就是种子了
                # 这里要做的事情有
                # 1. 请求一个cookie
                # 2. 完成html的请求
                # 3. data放入psm队列里
                # 4. 反馈给seesion/seed模块
                seed = msg_dict
                # 调度spider

        time.sleep(0.1)


if __name__ == '__main__':
    listen_task_que()