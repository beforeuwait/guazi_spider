# coding=utf8

"""
    author: wangjiawei
    date:   2018-09-03

    # 种子管理模块，被调用时候完成:
        1. 生产种子
        2. 要cookie
        3. 派发种子

    # 2018-09-05 更改逻辑
        todo: 在派发种子一次丢固定的种子数量, 然后监听反馈队列
"""

import config
from config import logger
from config import redis_cli
from SeedsHandler import seeds_maker
from SeedsHandler import loads_seed_in_generator
from SeedsHandler import update_brands_serise
from utils import loads_json
from utils import dumps_json
from utils import wait_for_msg

class SeedsMangement():
    """种子管理器
    当slave调用该模块时候
    该slave就变成一个种子派发节点
    要做的事情:
    1. 生产种子
    2. 为种子匹配cookie\ 同SessionMangement通信
    3. 派发种子
    4. 接收反馈消息
    """

    def __init__(self):
        self.seeds_store = loads_seed_in_generator()

    def seeds_maker(self):
        """种子生产商
        在程序一开始时候被调度调用
        以一个顺序的方式放入种子池里
        """
        seeds_maker()

    def take_out_a_seed(self):
        """
        从生成器里取出一个种子
        之所以这样控制，seedMangement需要反馈
        每次投放固定量的种子
        """
        seed = None
        try:
            seed = loads_json(self.seeds_store.__next__())
        except:
            # 种子派发完毕
            logger.info('种子派发完毕')
        return seed

    def push_seed_2_queue(self, seed):
        """
        将拿到的seed放到队列里
        :return:
        """
        que = config.task_que
        redis_cli.lpush(que, dumps_json(seed))

    def decide_push_seed_2_queue(self, count):
        """拿到种子，将种子推入队列里"""
        is_break = False
        if count == 0:
            count = 20

        num = 1
        while num <= count:
            seed = self.take_out_a_seed()
            if not seed:
                is_break = True
                break
            self.push_seed_2_queue(seed)
            num += 1

        return is_break

    def deal_feed_back(self, msg):
        """
        消息传递过来就是种子信息，通过解析种子里的cookie_status
        如果cookie_status 为 1 就代表需要删除cookiel
        如果出现stop_sign， 则代表slave长时间没有拿到seed后，默认结束
        """
        is_deal = False
        if msg.get('cookie_status') == 1:
            # 这就代表要删除该种子要重新投放了
            # 开始处理
            is_deal = True
        return is_deal


    def seed_main_logic(self):
        """
        主要处理逻辑
        1. 生产种子
        2. 提取种子
        3. 检测状态
        """
        print('seed管理已启动')
        # 完成后像队里推送一条已完成启动
        que = config.task_que_fb
        ctx = dumps_json({'sedm': 'done'})
        redis_cli.lpush(que, ctx)

        # 更新车系
        update_brands_serise()
        # 第一步就是生产种子
        print('生产种子')
        self.seeds_maker()
        # 完了后先丢20个种子
        is_break = self.decide_push_seed_2_queue(0)

        # 开始监听队列，准备投放种子
        que_req = config.sed_req
        while not is_break:
            msg = wait_for_msg(que_req)
            if msg:
                # 开始处理这个反馈
                # 主要看 cookie_status
                is_deal = self.deal_feed_back(msg)
                if is_deal:
                    msg.update({'cookie_status': 0})
                    self.push_seed_2_queue(msg)
                    continue
                else:
                    # 通过的话，则上传一个新的种子
                    self.decide_push_seed_2_queue(1)


"""
    # 旧代码
    # 
    
    def take_out_a_seed(self):
        
        # 吐出一个种子
        # 同时记录偏移量
        # 同时做好，最后一个种子被拿出来
        
        offset = int(file_content(config.offset_file))
        try:
            seed = loads_json(self.seeds_store.__next__())
            overwrite_file(config.offset_file, str(offset + 1))

        except:
            logger.info('种子分派完毕')
            seed = None
            # 偏移量重置
            overwrite_file(config.offset_file, '1')

        return seed
    
    def full_seed_maker(self, cookie_list):
        # 生产种子
        # 从种子库拿种子
        # 从cookie库拿cookie
        # 每次生产的seed数据根据cookie来判断的
        # 需要一个偏移量来记录派发出几个种子
        # 生产一个种子, 种子分发完毕后seed = None
        seed = self.take_out_a_seed()
        # 拿到一个cookie同时和cookie的偏移量
        # todo: 向消息队列请求提交需求
        cookie_len = len(cookie_list)
        cookie_offset = self.cookie_offset_handler(cookie_len=cookie_len)
        # 更新种子
        seed.update({
            'cookie': cookie_list[cookie_offset]
        })

        return seed
    
    def cookie_offset_handler(self, cookie_len):
        
        # 拿到当前的cookie_offset，根据要求，返回当前/自增后的offset
        # 还要自动判断，当offset>cookie_len时候，自动复位
        
        offset = int(redis_cli.get('cookie_offset').decode())
        # 如果offset为空的时候，放入一个值 0, offset=cookie_len-1 代表cookie分派结束
        if offset is None or offset == cookie_len - 1:
            offset = 0
            redis_cli.set('cookie_offset', 0)
        else:
            # 接下来就是处理是否自增部分
            # 偏移量要自增 1
            offset += 1
            redis_cli.set('cookie_offset', offset)
        return offset
    
    def push_a_seed_2_queue(self, seed):
        # 将种子推入队列
        que = config.task_que
        redis_cli.lpush(que, dumps_json(seed))
        
    def main_logic(self):
        # 这里一切交给它去做

        # 09-04 主逻辑发生变化
        # seed mangement所承担的角色，就是单纯把种子放入任务队列里
        # 还要承担一个去重的功能

        # 首先是制造种子
        que_ssn_sed = config.ssn_sed_que
        self.seeds_maker()
        is_break = False
        # 制造完种子便开始派发种子
        while not is_break:
            is_break = self.seed_publish()
            # 完了后，等待反馈
            feed_back = self.seed_state_receive()
            if feed_back:
                # 处理反馈
                self.deal_feed_back(feed_back)
                is_break = True
            # 完了后，一轮后需要得到session的反馈
            msg = wait_for_msg(que_ssn_sed)
            #todo: 这里需要一个处理
 
    def seed_publish(self):
        # 播种
        is_break = False
        que_sed_ssn = config.sed_ssn_que
        que_ssn_sed = config.ssn_sed_que
        # 先和sessionMangement通信，拿到cookieList
        ctx = {'task': 'cookie_list'}
        redis_cli.lpush(que_sed_ssn, ctx)
        cookie_list = wait_for_msg(que_ssn_sed)
        # # 拿到cookie_list后开始装配种子
        # # 仍旧要重置offset
        redis_cli.set('cookie_offset', 0)
        # 每次派发长度根据cookie_list来
        for i in cookie_list:
            seed = self.full_seed_maker(cookie_list)
            if seed:
                self.push_a_seed_2_queue(seed)
            else:
                is_break = True
        return is_break

    def seed_state_receive(self):
        #获取种子的状态
        #返回一个列表
        
        que = config.task_que_fb
        feed_back = wait_for_msg_list(que)
        return feed_back

    def deal_feed_back(self, feed_back):
        # 处理反馈
        # 该删号就删号
        
        que_sed_ssn = config.sed_ssn_que
        que_ssn_sed = config.ssn_sed_que
        seed_list = loads_json(translate_2_json_dict(feed_back))
        user_id = []
        for each in seed_list:
            if each.get('cookie_status') == '1':
                user_id.append(each.get('userid'))
        ctx = {'task': 'delete_id', 'userid': user_id}
        redis_cli.lpush(que_sed_ssn, ctx)
        # 然后就是等待session节点去处理了
        return
"""
