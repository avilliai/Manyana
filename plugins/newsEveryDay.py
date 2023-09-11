import datetime
import os.path
import random

import httpx
import asyncio

import requests
from PIL import Image
from io import BytesIO


def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers
async def news():
    url="http://bjb.yunwj.top/php/tp/60.jpg"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    #path="./news.png"
    path="data/pictures/cache/"+time+"news.png"
    if os.path.exists(path):
        return path
    else:
        #r=requests.get(url).content
        #with open("./news.png","wb") as fp:
            #fp.write(r)
            #return
        #async with httpx.AsyncClient(timeout=20) as client:
            #r = await client.get(url)
            #url=r.json().get("tp1")
            #print(url)
            #return url
            #print(r.json().get("data").get("image")) # 从二进制数据创建图片对象
        async with httpx.AsyncClient(timeout=200,headers=get_headers()) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            #print(path)
            return path
async def moyu():
    headers = get_headers()
    url="https://moyu.qqsuu.cn/"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    path="data/pictures/cache/"+time+"moyu.png"
    #path="moyu.png"
    if os.path.exists(path):
        return path
    else:
        async with httpx.AsyncClient(timeout=20,headers=headers) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            #print(path)
            return path
async def xingzuo():
    url="https://dayu.qqsuu.cn/xingzuoyunshi/apis.php"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    # path="./news.png"
    path = "data/pictures/cache/" + time + "xingzuo.png"
    #path="./xingzuo.png"
    if os.path.exists(path):
        return path
    else:

        # print(r.json().get("data").get("image")) # 从二进制数据创建图片对象
        async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            #rint(path)
            return path
async def nong(url,name):
    # path="./news.png"
    path = "data/Elo/"+name+".png"
    # path="./xingzuo.png"
    if os.path.exists(path):
        return path
    else:

        # print(r.json().get("data").get("image")) # 从二进制数据创建图片对象
        async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            # rint(path)
            return path
async def sd(url,path):
    # path="./news.png"

    # path="./xingzuo.png"
    # print(r.json().get("data").get("image")) # 从二进制数据创建图片对象

    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # rint(path)
        return path
if __name__ == '__main__':
    asyncio.run(xingzuo())
