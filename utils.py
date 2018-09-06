# coding=utf8


import os
import time
import json
from config import logger
from lxml import etree
from config import redis_cli


# 重置文件

def initial_file(file_path):
    """
    指定path的文件，重置
    对于空文件，则创建
    :return:
    """
    path = os.path.abspath(file_path)
    if not os.path.exists(path):
        f = open(path, 'a')
        f.close()
    else:
        f = open(path, 'w')
        f.close()
    return

# 追加写入

def write_2_file(file_path, ctx):
    """
    向指定目录写入文件
    :param path: 路径
    :param ctx: 内容
    :return:
    """
    path = os.path.abspath(file_path)
    with open(path, 'a', encoding='utf8') as f:
        f.write(ctx + '\n')
    return

# 覆盖写入

def overwrite_file(file_path, ctx):
    """
    向指定目录写入文件
    :param path: 路径
    :param ctx: 内容
    :return:
    """
    path = os.path.abspath(file_path)
    with open(path, 'w', encoding='utf8') as f:
        f.write(ctx)
    return

# 解析json

def loads_json(json_text):
    """
    解析json
    :param json_text:
    :return:
    """
    js_dict = None
    try:
        js_dict = json.loads(json_text)
    except:
        logger.warning('json\tloads\t出错，请检查')
    return js_dict

# 写入json

def dumps_json(json_dict):
    return json.dumps(json_dict, ensure_ascii=False)

# 返回文本内容

def file_content(file_path):
    """返回文本内容
    如果是空文档呢
    """
    path = os.path.abspath(file_path)
    if not os.path.exists(path):
        f = open(path, 'w')
        f.close()
    return open(path, 'r', encoding='utf8').read()

# 解析lxml

def parse_lxml(html):
    """解析html"""
    selector = None
    try:
        selector = etree.HTML(html)
    except:
        logger.warning('lxml解析html时候出错')
    return selector

# 返回一个集合

def make_set(file_path, index, blank):
    """
    返回指定目录的集合
    :param file_path: 文件目录
    :param index: 索引位置
    :param blank: 分隔符
    :return:
    """
    path = os.path.abspath(file_path)
    if index != '' and blank != '':
        return set(i.strip().split(blank)[index] for i in open(path, 'r', encoding='utf8'))
    elif index == '' and blank != '':
        return set(i.strip().split(blank) for i in open(path, 'r', encoding='utf8'))
    else:
        return set(i.strip() for i in open(path, 'r', encoding='utf8'))

# 返回一个列表

def make_list(file_path, index, blank):
    """
    返回指定目录的集合
    :param file_path: 文件目录
    :param index: 索引位置
    :param blank: 分隔符
    :return:
    """
    path = os.path.abspath(file_path)
    if index != '' and blank !='':
        return [i.strip().split(blank)[index] for i in open(path, 'r', encoding='utf8')]
    elif index == '' and blank != '':
        return [i.strip().split(blank) for i in open(path, 'r', encoding='utf8')]
    else:
        return [i.strip() for i in open(path, 'r', encoding='utf8')]

# 返回一个生成器

def make_generator(file_path, blank):
    """
    返回一个生成器
    :param file_path:文件目录
    :param blank: 分隔符
    :return:
    """
    path = os.path.abspath(file_path)
    for i in open(path, 'r', encoding='utf8'):
        if blank != '':
            yield i.strip().split(blank)
        else:
            yield i.strip()

# translate

def translate_2_json_dict(ctx):
    """把redis返回的字符变成json能loads的字符串"""
    return ctx.decode().replace('\'', '"')


# redis

def wait_for_msg(que):
    """等待指定队列返回的数据
    todo :后期添加一个时间约束
    """
    redis = redis_cli
    start = time.time()
    data = None
    while True:
        if redis.exists(que):
            msg = redis.rpop(que)
            data = loads_json(translate_2_json_dict(msg))
            data = loads_json(data)
            break
        time.sleep(0.1)
        now = time.time()
        if now - start > 30:
            break
    return data

def wait_for_msg_long(que):
    """等待指定队列返回数据
    不停的等
    """
    redis = redis_cli
    while True:
        if redis.exists(que):
            msg = redis.rpop(que)
            data = loads_json(msg)
            break
        time.sleep(0.1)

    return data

def wait_for_msg_list(que, count):
    """等待指定队列返回的数据列表
    还有个指定的列表长度
    这里有个时间约束
    等待最多30秒

    # 09-05 这里发现一个bug，就是无论是否有数据都要等30秒
    当列表达到count or 30秒后， 这里都循环结束
    """
    start = time.time()
    data = []
    redis = redis_cli
    while True:
        if redis.exists(que):
            msg = redis.rpop(que)
            data.append(loads_json(translate_2_json_dict(msg)))
            if len(data) == count:
                break
        time.sleep(0.1)
        now = time.time()
        if now - start > 30:
            break

    return data
