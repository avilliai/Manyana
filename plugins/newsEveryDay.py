import asyncio
import datetime
import os.path
from io import BytesIO

import httpx
from PIL import Image

from plugins.toolkits import random_str, get_headers


async def news():
    time = datetime.datetime.now().strftime('%Y-%m-%d')
    url = f"https://cdn.xxhzm.cn/v2api/cache/60s/{time}.jpg"
    print(url)
    #path="./news.png"
    p = "data/pictures/cache/" + time + "news.jpg"

    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        with open(p, "wb") as f:
            f.write(r.content)
        return p


async def chaijun():
    headers = get_headers()
    url = "http://api.yujn.cn/api/chaijun.php?"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # print(path)
        return path


async def beCrazy(aim):
    headers = get_headers()
    url = f"https://api.lolimi.cn/API/fabing/fb.php?name={aim}"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        r = await client.get(url)
        r = r.json().get("data")
        # print(path)
        return r


async def danxianglii():
    headers = get_headers()
    time = datetime.datetime.now().strftime('%Y/%m%d')
    url = f"https://img.owspace.com/Public/uploads/Download/{time}.jpg"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=20, headers=headers) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # print(path)
        return path


async def moyu():
    headers = get_headers()
    time = datetime.datetime.now().strftime('%Y%m%d')
    url = f"https://dayu.qqsuu.cn/moyurili/file/{time}.png"
    
    p = "data/pictures/cache/" + time + "moyu.png"
    #path="moyu.png"

    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(url)
        with open(p, "wb") as f:
            f.write(r.content)
        return None


async def xingzuo():
    url = "https://dayu.qqsuu.cn/xingzuoyunshi/apis.php"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    # path="./news.png"
    path = "data/pictures/cache/" + time + "xingzuo.png"
    #path="./xingzuo.png"
    # print(r.json().get("data").get("image")) # 从二进制数据创建图片对象
    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        return None
        #return path


async def nong(url, name):
    # path="./news.png"
    path = "data/Elo/" + name + ".png"
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


async def sd(url, path):
    # path="./news.png"

    # path="./xingzuo.png"
    # print(r.json().get("data").get("image")) # 从二进制数据创建图片对象

    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # rint(path)
        return path


async def handwrite(msg):
    url = f"https://zj.v.api.aa1.cn/api/zuoye/?msg={msg}"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # rint(path)
        return path
async def bingEveryDay():
    url="https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=zh-CN"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        text=r.json()["images"][0]["title"]+"\n"+r.json()["images"][0]["copyright"]
        url="https://cn.bing.com"+r.json()["images"][0]["url"]
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)
        return text,path
if __name__ == '__main__':
    asyncio.run(xingzuo())
