# coding=utf8

"""
    瓜子登录模块

"""

from selenium import webdriver
import time
import logging
import config
from config import logger
from utils import initial_file
from utils import write_2_file
from utils import dumps_json

log = logging.getLogger('main')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('user.log')
fmt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)

# 登录部分

def lets_login():
    """
    完成登录，并输出cookie
    :return: 该用户的cookie
    """
    brower = webdriver.Firefox(executable_path='./source/geckodriver')

    url = config.home_page_url

    xpath = config.log_in_xpath
    brower.get(url)

    # 关闭广告

    # 首先看广告是否出现
    try:
        adv2 = brower.find_element_by_xpath(xpath.get('adv2'))
        adv2.click()
    except:
        pass

    # 然后点击登录
    log_btn = brower.find_element_by_xpath(xpath.get('log_btn'))
    log_btn.click()

    # 输入账号
    phone = input('请输入登录手机号:\t')
    is_ok = True
    while is_ok:
        try:
            phone_number = brower.find_element_by_xpath(xpath.get('phone_number'))
            phone_number.send_keys(str(phone))
            is_ok = False
        except Exception:
            print('在输入手机号出错，重试....\t')
            time.sleep(3)

    print('\t已输入手机号\t')

    # 点击获取验证码
    print('\t准备点击验证码\t')
    is_captcha_ok = True
    while is_captcha_ok:
        try:
            captcha_btn = brower.find_element_by_xpath(xpath.get('captcha_btn'))
            captcha_btn.click()
            print('验证码已发送,请查看手机')
            is_captcha_ok = False
        except Exception:
            print('验证码发送失败,重试......\t')
            time.sleep(3)

    # 输入验证码
    captcha_code = input('请输入验证码:\t')
    captcha_is_ok = True
    while captcha_is_ok:
        try:
            captcha_input = brower.find_element_by_xpath(xpath.get('captcha_input'))
            captcha_input.send_keys(str(captcha_code))
            captcha_is_ok = False
        except Exception:
            print('验证输入过程错误,重试....\t')
            time.sleep(3)

    # 登录
    is_login_ok = True
    print('准备登录....')
    while is_login_ok:
        try:
            commit_btn = brower.find_element_by_xpath(xpath.get('commit_btn'))
            commit_btn.click()
            print('已点击登录')
            is_login_ok = False
        except Exception:
            print('未找到相关元素，登录失败,重试....\t')

    # 时已至此，登录结束，是否成功需要看cookie里字段信息
    """userid guaZiUserInfo GZ_TOKEN """
    cookies = brower.get_cookies()

    brower.quit()

    return cookies

# cookie提取部分

def lets_get_cookie(cookies):
    # result 用来验证cookie 从而验证登录是否成功
    result = False
    index_list = ['userid', 'guaZiUserInfo', 'GZ_TOKEN']
    user_info = {}
    for each in cookies:
        for i in index_list:
            if each.get('name') == i:
                result = True
                user_info.update({i: each.get('value')})

    if result:
        # 保存账号
        write_2_file('DB/user_info.txt', dumps_json(user_info))
        print('该用户信息已经保存')
    else:
        print('登录失败,未能保存用户cookie信息')

# 主逻辑部分

def main_theme():
    # 主逻辑部分
    print('##############################################')
    print('#                                            #')
    print('#                                            #')
    print('#             开始手机用户登录信息              #')
    print('#                                            #')
    print('#                                            #')
    print('##############################################\n\n\n\n')

    # 清理之前的用户文件
    initial_file('DB/user_info.txt')

    while True:
        print('选择操作\n\t 1:添加用户\n\t 2: 退出\n\n')
        log.info('触发用户-添加功能')
        choice = input('请输入选择:\t')
        if choice == '1':
            # 添加用户
            cookies = lets_login()
            lets_get_cookie(cookies)
            print('********************')
            print('*    是否继续操作    *')
            print('********************\n\n')
            continue
        else:
            break



if __name__ == '__main__':
    main_theme()