# coding=utf8

"""
    author  : wangjiawei
    date    : 09-05

    由Slave接受到种子,然后调度该脚本，完成数据请求
    请求后的数据
"""


def receive_seed_and_start_crawl(seed):
    """接受种子
    拿出url
    带cookie
    完成请求
    """