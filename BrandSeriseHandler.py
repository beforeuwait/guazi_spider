# coding=utf8

"""
    author = wangjiawei
    date = 2018/07/09

    该脚本为获取瓜子上全部汽车品牌以及车系的数据
"""

from utils import write_2_file
from utils import loads_json
from utils import parse_lxml
from utils import make_set
from utils import make_generator
from HTTP.RequestServerApi import RequestAPI


brands_url = 'https://www.guazi.com/bj/sell/'

serise_url = "https://www.guazi.com/node/clientUc/brand/series?brandId={0}&needChild=0"

brands_file = './DB/all_brands.csv'

serise_file = './DB/all_serise.csv'

headers = {
    "Connection": "keep-alive",
    "Host": "www.guazi.com",
    "Referer": "https://www.guazi.com/bj/sell/?clueS=01",
    "transUrl": "clientUc/brand/series",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
}


def get_all_brands():
    """增量更新所有的汽车品牌"""

    id_set = make_set(brands_file, 0, '\t')
    session = RequestAPI()
    html = session.receive_and_request(url=brands_url, headers=headers, method='GET')
    del session
    if html != 'null_html':
        data = parse_html(html)
        save_data(data, id_set)

def parse_html(html):
    selector = parse_lxml(html)
    data = []
    if selector is not None:
        brands_list = selector.xpath('//ul[@class="all-brand"]/li')
        for brand in brands_list:
            brand_id = brand.xpath('@data-id')[0]
            brand_name = brand.xpath('text()')[0]
            data.append([brand_id, brand_name])
    return data

def save_data(data, id_set):
    for each in data:
        if each[0] not in id_set:
            ctx = '\t'.join(each)
            write_2_file(brands_file, ctx)


def get_all_serise():
    """
    获取所有车系
    :return:
    """
    id_set = make_set(serise_file, 2, '\t')
    all_brands = make_generator(brands_file, blank='\t')
    session = RequestAPI()
    for each in all_brands:
        url = serise_url.format(each[0])
        html = session.receive_and_request(url=url, headers=headers, method='GET')
        if html != 'null_html':
            data = parse_json(html)
            if data != []:
                save_serise_data(each[0], each[1], data, id_set)

def parse_json(html):
    """解析车系的数据"""
    js_dict = loads_json(html)
    data = []
    if js_dict is not None:
        for each in js_dict.get('data'):
            id = each.get('id')
            name = each.get('name')
            # url = each.get('url')
            guochanhezijinkou = each.get('guochanhezijinkou')
            data.append([id, name, guochanhezijinkou])
    return data

def save_serise_data(bid, bname, data, id_set):
    """保存车系的数据"""
    for each in data:
        if each[0] not in id_set:
            ctx = '\t'.join([bid, bname, each[0], each[1], each[2]])
            write_2_file(serise_file, ctx)


def main_get_brands_serises():
    """主逻辑"""
    print('开始更新品牌')
    get_all_brands()
    print('开始更新车系')
    get_all_serise()