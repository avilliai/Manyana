import json

import requests

from plugins.newsEveryDay import get_headers
async def arkSign(url):
    url=f"https://api.lolimi.cn/API/ark/a2.php?img={url}"

    r=requests.get(url,timeout=20)
    #print(r.text)
    #print(r.text,type(r.json()))
    return str(r.text)
#arkSign("https://img.xjh.me/random_img.php")