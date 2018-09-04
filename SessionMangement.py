# coding=utf8

"""
    author: wangjiawei
    date:   2018-09-03

    # 响应党的号召，给schedule减负
    # 由slave节点来调用该模块，从而开始sessoin之路

"""

import os
import config
from config import redis_cli
from LoginHandler import main_theme
from utils import initial_file
from utils import loads_json
from utils import dumps_json
from utils import write_2_file
from utils import make_list
from utils import wait_for_msg_list


class SessionMangement():
    """
    session管理器
    提供2个功能
        1. 添加新用户
        2. 删除无效的用户
        # 08-30
        # 添加一个api 用来调用cookie
        # 09-03
        # 添加redis模块
    """

    def __add_cookie(self):
        """
        登录模块
        :return:
        """
        main_theme()
        return

    def __delete_cookie(self, user_id):
        """
        这里是删除思路就是遍历一遍cookie_list
        除开删除的用户，其余重新写入文件里
        :param user_id:待删除的 user_id
        """
        cookie_list = self.load_cookies_list()
        new_cookie_list = []
        for cookie in cookie_list:
            cookie = loads_json(cookie)
            if not cookie.get('userid') == user_id:
                new_cookie_list.append(cookie)
        # 重新写入文件
        initial_file(config.user_info_file)
        if new_cookie_list != []:
            for each in new_cookie_list:
                write_2_file(config.user_info_file, dumps_json(each))
        return

    def __is_cookie_empty(self):
        """检查文件里cookie状态
        提交给上层，决定是否追加用户
        """
        is_empty = False
        path = config.user_info_file
        if not os.path.getsize(path):
            is_empty = True
        return is_empty

    def __check_and_add_cookie(self):
        """检查文件
        是否添加新用户
        """

        is_empty = self.__is_cookie_empty()
        if is_empty:
            # 需要添加用户
            self.__add_cookie()

    def __check_and_delete_cookie(self, user_id):
        """检查文件
        如果用户为0，这里需要去调 add_cookie
        :param user_id:
        :return:
        """
        is_empty = self.__is_cookie_empty()
        if not is_empty:
            # 不是空，则可以删除用户
            self.__delete_cookie(user_id)

        # 删除后，仍然要验证,如果为空了，则添加用户
        self.__check_and_add_cookie()
        return

    def logic_add_cookie(self):
        """外部调用的逻辑模块
        添加cookie
        """
        self.__check_and_add_cookie()

    def logic_delete_cookie(self, user_ids):
        """外部调用的逻辑模块
        删除指定的cookie
        :param user_ids: 待删除列表
        """
        for user_id in user_ids:
            self.__check_and_delete_cookie(user_id)

    def load_cookies_list(self):
        """返回cookie列表
        交给schedule去调用
        seed合并cookie放入队列里
        """
        cookie_list = make_list(file_path=config.user_info_file, index='', blank='')
        return cookie_list

    def choos_a_cookie(self, slave_count):
        """设置一个偏移量
        用来提取一个cookie
        """
        offset = int(redis_cli.get('cookie_offset').decode())
        # 如果offset为空的时候，放入一个值 0, offset=cookie_len-1 代表cookie分派结束
        if offset is None or offset == slave_count - 1:
            offset = 0
            redis_cli.set('cookie_offset', 0)
        else:
            # 接下来就是处理是否自增部分
            # 偏移量要自增 1
            offset += 1
            redis_cli.set('cookie_offset', offset)
        return offset

    def put_cookie_2_que(self, cookie):
        """
        将cookie放入队列里
        """
        que = config.ssn_rep
        redis_cli.lpush(que, dumps_json(cookie))

    def deal_feed_back(self, msg_list):
        """
        消息传递过来就是种子信息，通过解析种子里的cookie_status
        如果cookie_status 为 1 就代表需要删除cookiel
        如果出现stop_sign， 则代表slave长时间没有拿到seed后，默认结束
        """
        is_break = False
        userid_list = []
        for each in msg_list:
            if each.get('cookie_status') == 1:
                # 这就代表要删除id了
                userid = each.get('cookie').get('userid')
                userid_list.append(userid)
            elif each.get('stop_sign'):
                is_break = True
        # 开始处理
        if userid_list:
            self.logic_delete_cookie(userid_list)

        return is_break

    def session_main_logic(self):
        """
        由slave调用的部分
        实例化后，实现登录
        在 删除,导入列表时候通过消息通信来完成
        需要加一个结束模块
        """
        # 实例化我们的种子模块,并开始登录
        self.logic_add_cookie()
        # 完成后像队里推送一条已完成
        que = config.task_que
        ctx = dumps_json({'session': 'done'})
        redis_cli.lpush(que, ctx)
        # 开始监听反馈队列
        ssn_req = config.ssn_req
        is_break = False
        while not is_break:
            # 监听ssn_req队列，根据消息的条数，发放对应数量的cookie
            msg_list = wait_for_msg_list(ssn_req)

            # todo: 处理消息里的东西，比如删除id
            is_break = self.deal_feed_back(msg_list)
            if is_break:
                break
            # todo: 处理消息条数
            # slave_count 当前需要cookie 的个数
            slave_count = len(msg_list) if msg_list else 1
            cookie_list = self.load_cookies_list()

            # 开始之前将cookie_offset 置空
            redis_cli.set('cookie_offset', slave_count)
            while slave_count > 0:
                # 相应的放对应的cookie数到队列里
                current_offset = self.choos_a_cookie(slave_count)
                cookie = cookie_list[current_offset]
                # 放入队列:
                self.put_cookie_2_que(cookie)
                slave_count -= 1



"""
        # 这里的处理逻辑发生变化
        # 每次统计需要的session数量
        # 根据统计数据，丢相应的数量的cookie到ssn_rep队列里
        while True:
            if redis_cli.exists(ssn_req):
                msg = redis_cli.rpop(ssn_req)
                msg_dict = loads_json(translate_2_json_dict(msg))
                task = msg_dict.get('task')
                if task == 'delete_id':
                    # 删除cookie
                    user_id = msg_dict.get('userid')
                    if user_id:
                        # 针对user_id是空集时候的情况
                        self.logic_delete_cookie(user_id)
                    # 告知已完成
                    ctx = 'delete_id_done'
                    redis_cli.lpush(ssn_rep, ctx)
                elif task == 'cookie_list':
                    # 返回cookie列表
                    cookie_list = self.load_cookies_list()
                    # 放入消息队列里
                    redis_cli.lpush(ssn_rep, dumps_json(cookie_list))
                else:
                    # 中止程序，退出
                    break
            time.sleep(0.1)
"""


