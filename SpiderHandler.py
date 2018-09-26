# coding=utf8

"""
    author  : wangjiawei
    date    : 09-05

    由Slave接受到种子,然后调度该脚本，完成数据请求
    请求后的数据

    09-10: 请求过程反复出现 status_code > 300 的问题
            第一次求cookie时候，不要顺带求seed

    09-25:
        todo: 遇到反馈的cookie比请求的多，这里需要修改，逻辑也需要修改
        请求方式从session变回request
    09-26:
        请求单独拿出来


"""

import re
import os
import time
import random
import config
from config import redis_cli
from copy import deepcopy
import HTTP.requests_server_config as scf
from HTTP.requests_server_config import logger
from HTTP.requests_server_config import filter_dict
from HTTP.RequestServerApi import RequestAPI
from utils import dumps_json
from utils import wait_for_msg_long
from utils import parse_lxml


headers = config.headers
ua_list = config.ua_list

# 使用到的队列

ssn_2_slv = config.ssn_2_slv

slv_2_ssn = config.slv_2_ssn

slv_2_sed = config.slv_2_sed

slv_2_psm = config.slv_2_psm

class RequestModel(RequestAPI):
    """
    继承RequesAPI
    自定义请求过程....

    """
    def __init__(self, mark):
        super(RequestModel, self).__init__()
        self.js_file = './js/js_{0}.js'.format(mark)

    def user_define_request(self, url, cookie_info):
        """
        因为瓜子的请求按照以下流程
        访问页面
            203：需要验证
            200：拿到数据
            302：cookie失效
        所以 status_code很重要
        """

        # 先更新请求头
        headers.update({'User-Agent': random.choice(ua_list)})
        self.update_headers(headers)
        # 更新cookie
        # self.update_cookie_with_outer({"userid": cookie_info.get("userid"),
        #                                "guaZiUserInfo": cookie_info.get('guaZiUserInfo'),
        #                                "GZ_TOKEN": cookie_info.get("GZ_TOKEN")})
        # 2018-09-25更新,直接更新所给的cookie
        self.update_cookie_with_outer(cookie_info)
        retry = config.request_retry
        data = []
        while retry > 0:
            # 开始请求
            html, status_code = self.do_request(url=url, method="GET", params=None, payloads=None)
            print('重试\t{0}\t状态码\t{1}'.format(retry, status_code))
            # 开始判断
            if status_code < 300:
                # 这里分两种处理
                if status_code == 203:
                    # 走验证
                    self.deal_js(html)
                    # 然后再次请求
                    time.sleep(1)
                    retry -= 1
                    continue
                else:
                    # 拿数据
                    data = self.spider_parse(html)
                    break
            elif status_code > 300 and status_code < 400:
                # 说明该cookie失效
                # 反馈回去
                data = ['redirect']
                # 失效，重试
                time.sleep(random.random()*10)
                break
            else:
                data = ['null']
            retry -= 1

        # 清理cookie
        self.discard_cookies()

        return data

    def do_request(self, url, method, params, payloads):
        """重写这部分"""
        retry = scf.retry
        html = 'null_html'
        response = None
        status_code = 400
        while retry > 0:
            try:
                # 选择执行的方式
                if method == 'GET':
                    # 请求前判断是否有参数，有的话添加到session里,请求后则删除
                    self.update_params(params)
                    response = self.GET_request(url)
                    self.discard_params()

                elif method == 'POST':
                    response = self.POST_request(url, payloads)

            except Exception as e:
                # 输出log, 这里的错误都是网络上的错误
                # logger.info('请求出错, 错误原因:', exc_info=True, extra=filter_dict)
                logger.info('请求出错, 错误原因:\t{0}'.format(e), extra=filter_dict)
                retry -= 1

            # 要重新判断status
            # 拿到response后，处理
            if response is not None:
                status_code = response.status_code
                html = response.content.decode('utf8')
                break
            retry -= 1
        return html, status_code

    def deal_js(self, html):
        """处理js，解析token
        """
        js = re.findall('<script type="text/javascript">(.*?)</script>', html, re.S)
        if js:
            if "xredirect" in js[0]:
                js_text = js[0].replace("xredirect(name,value,url,'https://')", "console.log(value)")

                # 存js
                with open(self.js_file, 'w', encoding='utf8') as f:
                    f.write(js_text)
                    f.write('phantom.exit(0)')

                # 更新session
                path = os.path.abspath(self.js_file)
                cmd = "phantomjs {0}".format(path)
                antipas = os.popen(cmd).read().strip()
                # 更新cookie
                self.update_cookie_with_outer({"antipas": antipas})

        return

    def spider_parse(self, html):
        """先判断有没有数据"""
        selector = parse_lxml(html)
        data = []
        if selector is not None:
            # 先看是否有数据
            car_list = selector.xpath('//ul[@class="deal-list clearfix"]/li')
            if car_list:
                for each in car_list:
                    src = each.xpath('img/@src')[0]
                    title = each.xpath('h2[@class="deal-p1"]/text()')[0].replace('\n', '')
                    info = each.xpath('p[@class="deal-p2"]/text()')[0].replace(' ', '').replace('\n', '').split('|')
                    type_year = info[0]
                    distance = info[1]
                    city = info[2]
                    indv_price = each.xpath('p[@class="deal-p3"]/em/text()')[0]
                    dealer_price = each.xpath('p[@class="deal-p3"]/i/text()')[0]
                    # todo 新情况，这里有千这个单位
                    try:
                        if '万' in indv_price:
                            i_price = float(indv_price.replace('万', ''))
                        else:
                            i_price = float(indv_price.replace('元', '').replace('千', '')) / 10

                        if '千' in dealer_price:
                            d_price = float(dealer_price.replace('千元', '')) / 10
                        else:
                            d_price = float(dealer_price.replace('万元', ''))
                        dealer_price = str(i_price - d_price) + '万'
                    except:
                        pass
                    data.append([src, title, type_year, distance, city, indv_price, str(dealer_price)])
        return data



class SpiderHandler():
    """继承RequAPI 是因为要使用其diy的方法"""

    def __init__(self, mark):
        super(SpiderHandler, self).__init__()
        self.mark = mark
        self.js_file = './js/js_{0}.js'.format(mark)

    def demo(self, seed, cookie):
        url = seed.get('url')
        rm = RequestModel(self.mark)
        data = rm.user_define_request(url, cookie)
        print(data)

    def receive_seed_and_start_crawl(self, seed):
        """接受种子
        拿出url
        带cookie
        完成请求
        """

        print('\nspider获取任务')
        url = seed.get('url')
        # 一个反馈，请求一个cookie
        print('请求种子和cookie')

        self.feed_back_seed(seed, session=True, seed=False)

        # 等待cookie
        cookie = wait_for_msg_long(ssn_2_slv)

        # 实例化请求，解析模块
        rm = RequestModel(self.mark)
        data = rm.user_define_request(url, cookie)

        # 首先验证data是有有效
        if data != ['redirect'] and data != ['null'] and data != []:
            # 先反馈, 这时候只需要向种子管理反馈
            self.feed_back_seed(seed, session=False, seed=True)
            # 放数据
            seed.update({'data': data})
            # 丢入持久化队列里
            print('有数据,放入持久化队列\n')
            redis_cli.lpush(slv_2_psm, dumps_json(seed))

        elif data == ['redirect']:
            # 反馈该cookie失效, 需要向两个队列同时反馈
            seed_b = deepcopy(seed)
            seed_b.update({'cookie_status': 1})
            # 这里犯了一个大错，就是cookie呢  09/10
            seed_b.update({'cookie': cookie})
            # 丢入反馈队列里
            self.feed_back_seed(seed_b, session=True, seed=True)
            print('cookie失效,完成反馈\n')
            del seed_b

        else:
            # 没有数据，cookie仍旧是有效的
            # 只需要向种子管理反馈
            self.feed_back_seed(seed, session=False, seed=True)
            print('没有数据, 完成反馈\n')

        # 他的生命循环完成
        del seed
        del rm


    def feed_back_seed(self, ctx, session, seed):
        """向seesion和seed管理反馈
            session=True时候，需要向session管理发送
            seed=True时候，需要向seed管理推送
        """
        if session and seed:
            redis_cli.lpush(slv_2_sed, dumps_json(ctx))
            redis_cli.lpush(slv_2_ssn, dumps_json(ctx))
        elif session and not seed:
            redis_cli.lpush(slv_2_ssn, dumps_json(ctx))
        else:
            redis_cli.lpush(slv_2_sed, dumps_json(ctx))
        return


# if __name__ == '__main__':
#     seed = {"brand_id": "1199", "brand": "奥迪", "serise_id": "2614", "serise": "奥迪A5", "p_type": "合资", "url": "https://www.guazi.com/xinyang/dealrecord?tag_id=22288&date=2017100", "check_city": "xinyang", "date": "2018-1", "cookie": {}, "data": [], "cookie_status": 0, "epoh": 0}
#     cookie = {"clueSourceCode": "%2A%2300", "preTime": "%7B%22last%22%3A1537928136%2C%22this%22%3A1537928136%2C%22pre%22%3A1537928136%7D", "GZ_TOKEN": "ef52toYlCiG36xYV8f3011%2BZVJgkcTK8eTkkn31WYGulmX9gKIByhmHZp1d6sg%2BtwJ3L0CbW2avGHetiKQLSM5EvM90l2XbOHFMZs97irvp8flsdbMTJlK1okNg8BAtx6RkhoQ%2BhbwYPAaLDLw", "guaZiUserInfo": "0MSnBkg0hdYQNXvlLOYi2", "userid": "620499844"}
#     sh = SpiderHandler('1')
#     # sh.receive_seed_and_start_crawl(seed)
#     sh.demo(seed, cookie)