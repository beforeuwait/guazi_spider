  # coding=utf8

"""  
    author: wangjiawei
    date: 2018/07/09

    TODO LIST:
    1. GeneralRequest
    2. RequestAPI
    3. test_unit

    #############################################################################
    # updatetime: 2018/08/07    添加selenium 模块，驱动firefox (个人感觉firefox稳定些)
    # 提供思路: 2018/08/15
    # 1. 支持app抓取，比如 appium
    # 2. 提供http/2的扩展, 熟读hyper谢谢
    # 3. 针对比如淘宝对selenium的封杀，熟读selenium底层

    ##############################################################################
    # updatetime: 2018/08/23
    新的思路，
    保持程序的蠢
    error应该抛出交给上层去处理

"""
import requests
import HTTP.requests_server_config as scf
from HTTP.requests_server_config import logger, filter_dict


class GeneralRequest():
    """请求模块
    
    承载了大部分功能
    """

    def __init__(self):
        # 初始化的时候就创建session,并带上proxy
        self.s = self.establish_session()
        # 默认是带了代理的
        self.update_proxy()
    
    def establish_session(self):
        """创建一个session

        session在笔者看来就是cookie管理
        使用session的目的在于，容易操作cookie
        """
        return requests.Session()
    
    def cloes_session(self):
        """关闭session

        针对页面跳转，会出现打开新的session，
        当前的session也应该相应的关闭
        关闭所有adapter(适配器) such as the session
        """
        self.s.close()
        return 

    def GET_request(self, url):
        """执行get请求

        首先是判断是否有参数
        默认是不允许跳转的
        """
        """
        response = self.s.get(url, params=params, allow_redirects=False) \
                    if params is not None \
                    else self.s.get(url, allow_redirects=False)
        # 带参和不带参的处理放到请求发起的地方，这个函数就是纯粹的发起一次请求而已
        """
        response = self.s.get(url, allow_redirects=False, timeout=30)

        return response

    def POST_request(self, url, payloads):
        """执行post请求

        默认是不允许跳转的
        """

        response = self.s.post(url, data=payloads, timeout=30)

        return response
    
    def OTHER_request(self):
        """执行别的请求，后期添加
        
        接口留在这,比如 put, delete等
        """
        pass
    
    def update_cookie_with_response(self, cookie):
        """通过response这个对象去更新cookie

        **这里一个强制性的要求就是，请求后，更新cookie**

        这里需要关注，当请求的response是无效的
        更新cookie时候会报错，这里需要一个错误提示
        """
        try:
            self.s.cookies.update(cookie)
        except:
            # TODO 这里做一个日志输出
            logger.info("response更新cookie数据失败,可能请求失败", extra=filter_dict)
    
    def update_cookie_with_outer(self, cookies):
        """通过外部加载去更新cookie
        通常使用场景
        1. 带cookie绕过服务器验证
        2. 带cookie模仿用户去请求数据
        """

        self.s.cookies.update(cookies)
        return

    def update_headers(self, params):
        """通过外部传入headers更新自身的headers

        可以是更新headers里的某一个字段
        也可以是更新headers里的全部

        执行之前应该先把其session.headers.clear()
        """

        self.s.headers.clear()
        self.s.headers.update(params)
        return
    
    def update_proxy(self):
        """这个在默认的状态下是要携带代理的
        可以指定情况，不要代理
        """
        proxy = scf.proxy
        self.s.proxies.update(proxy)
        return
    
    def discard_proxy(self):
        """因为在默认的状态下，session是携带proxy了的
        该function就是在当前实例中取消代理
        """

        self.s.proxies.clear()
        return
    
    def discard_cookies(self):
        """discard all cookies
        删除/扔掉 所有cookie
        """
        self.s.cookies.clear_session_cookies()
        return
    
    def update_params(self, params):
        """为了简化请求过程
        将get请求的参数封装在这
        先判断params是否为空
        """
        if params is not None:
            self.s.params.update(params)
        return
    
    def discard_params(self):
        """删除当前session所携带的params
        """
        self.s.params.clear()
        return
    
    # def update_payloads(self, payloads):
    #     """将post请求里的参数更新到session中
    #     """
    #     self.s.data.update(payloads)
    #     return
    
    # def discard_payloads(self):
    #     """删除payloads
    #     """
    #     self.s.data.clear()
    #     return

    def do_request(self, url, method, params, payloads):
        """根据指定的请求方式去请求"""
        retry = scf.retry
        html = 'null_html'
        while retry > 0:
            response = None
            is_go_on = False
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
            
            # 拿到response后，处理 
            if response is not None:
                status_code = response.status_code
                is_go_on = self.deal_status_code(status_code)

                # 更新cookie
                self.update_cookie_with_response(response.cookies)

            if is_go_on:
                # 返回html
                try:
                    html = response.content.decode(scf.ec_u)
                except:
                    html = response.text
                break
            retry -= 1

        return html 
            

    def deal_status_code(self, status_code):
        """这个方法的意义在于服务器相应后，针对相应内容做处理

        2xx: 200是正常， 203正常响应，但是返回别的东西
        3xx: 重定向，在请求中已经规避了这部分
        4xx: 客户端错误
        5xx: 服务器错误
        """
        result = True
        if status_code >= 300 or status_code == 203:
            result = False
            # TODO: 添加logging
            logger.info('请求出现状态码异常:\t{0}'.format(status_code), extra=filter_dict)
        return result

 