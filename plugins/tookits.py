import os

import requests
import yaml

from plugins.newsEveryDay import get_headers
from lanzou.api import LanZouCloud
with open('config/api.yaml', 'r', encoding='utf-8') as f:
    apiYaml = yaml.load(f.read(), Loader=yaml.FullLoader)

lzy = LanZouCloud()
cookie = {'ylogin': str(apiYaml.get("蓝奏云").get("ylogin")), 'phpdisk_info': apiYaml.get("蓝奏云").get("phpdisk_info")}
code=lzy.login_by_cookie(cookie)

def fileToUrl(file_path,proxy):
    proxies = {
        "http://": proxy,
        "https://": proxy
    }
    url = "https://file.io"
    files = {"file": open(file_path, "rb")}
    response = requests.post(url, files=files,proxies=proxies,headers=get_headers())
    data = response.json()
    return data.get("link")
def lanzouFileToUrl(path):
    url=""
    def show_progress(file_name, total_size, now_size):
        percent = now_size / total_size
        bar_len = 40  # 进度条长总度
        bar_str = '>' * round(bar_len * percent) + '=' * round(bar_len * (1 - percent))
        print('\r{:.2f}%\t[{}] {:.1f}/{:.1f}MB | {} '.format(
            percent * 100, bar_str, now_size / 1048576, total_size / 1048576, file_name), end='')
        if total_size == now_size:
            print('')  # 下载完成换行

    def handler(fid, is_file):
        nonlocal url  # 声明要修改外部函数的url变量
        r=lzy.get_durl_by_id(fid)
        url=r.durl
    lzy.upload_file(path, -1, callback=show_progress,uploaded_handler=handler)
    return url