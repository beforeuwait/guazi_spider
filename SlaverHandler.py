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
        3. 接收普通请求任务，完成请求
            .1 需要同session管理节点通信
"""

import config
from config import redis_cli


