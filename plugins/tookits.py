import os

import requests

from plugins.newsEveryDay import get_headers


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