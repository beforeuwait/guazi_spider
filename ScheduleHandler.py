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

"""

import os
import redis
import config
from LoginHandler import main_theme
from config import logger
from SeedsHandler import seeds_maker
from SeedsHandler import loads_seed_in_generator
from utils import initial_file
from utils import overwrite_file
from utils import loads_json
from utils import dumps_json
from utils import file_content
from utils import write_2_file
from utils import make_list


