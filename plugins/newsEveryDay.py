import asyncio
import datetime
import os.path
import random
from io import BytesIO

import httpx
from PIL import Image

from plugins.RandomStr import random_str


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
    url = "https://api.52vmy.cn/api/wl/60s"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    #path="./news.png"
    path = "data/pictures/cache/" + time + "news.png"

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
    async with httpx.AsyncClient(timeout=200, headers=get_headers()) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        #print(path)
        return path


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
    url = "https://api.52vmy.cn/api/wl/moyu"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    path = "data/pictures/cache/" + time + "moyu.png"
    #path="moyu.png"

    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        #print(path)
        return path


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
        #rint(path)
        return path


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


if __name__ == '__main__':
    asyncio.run(xingzuo())
