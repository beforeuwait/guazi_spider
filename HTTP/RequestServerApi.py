# coding=utf8

"""
    author: wangjiawei
    date: 2018/07/09

"""

from HTTP.generalRequest import GeneralRequest

        
class RequestAPI(GeneralRequest):
    """这个类作为外部调用的api
    功能：
    """

    def __init__(self):
        # 实例化GeneralRequest 准备请求
        super(RequestAPI, self).__init__()

    def receive_and_request(self, **kwargs):
        """接收参数
        处理参数
        选择请求方式
        默认是带代理的
        """
        
        # 先获取参数， 目前就想了这么多
        url = kwargs.get('url')
        headers = kwargs.get('headers')
        method = kwargs.get('method')
        cookie = kwargs.get('cookie')
        params = kwargs.get('params')
        payloads = kwargs.get('payloads')
        
        # 构建请求头
        self.update_headers(headers)
        if cookie is not None:
            self.update_cookie_with_outer(cookie)

        # 开始请求
        html = self.do_request(url=url,
                                params=params, 
                                method=method, 
                                payloads=payloads)
        return html
    
    def user_define_request(self):
        """这个方法的意义在于用户自己去设计请求过程
        一般登录啊
        绕过js啊
        。。。
        都这这里自己定义
        """
        pass


"""
def temp_test_unit():
    \"""测试该库
    
    test_1: 
        url = 'http://www.baidu.com'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            "Host": "www.baidu.com",
            "Upgrade-Insecure-Requests": "1"
        }
    

    \"""
    url = 'http://www.baidu.com'
    headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            "Host": "www.baidu.com",
            "Upgrade-Insecure-Requests": "1"
        }
    api = RequestAPI()
    html = api.receive_and_request(url=url, headers=headers, method='GET')
    print(html)


if __name__ == '__main__':
    temp_test_unit()
"""