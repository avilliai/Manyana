import datetime
import os.path

import httpx
import asyncio

import requests
from PIL import Image
from io import BytesIO

async def news():
    url="https://api.emoao.com/api/60s"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    path="data/pictures/cache/"+time+"news.png"
    if os.path.exists(path):
        return path
    else:
        data={"type":"json"}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url,params=data)
            url=r.json().get("data").get("image")
            #print(r.json().get("data").get("image")) # 从二进制数据创建图片对象
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            return path
async def moyu():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
    }
    url="https://api.emoao.com/api/moyu"
    time = datetime.datetime.now().strftime('%Y_%m_%d')
    path="data/pictures/cache/"+time+"moyu.png"
    #path="moyu.png"
    if os.path.exists(path):
        return path
    else:
        data={"type":"json"}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(url,params=data)
            url=r.json().get("imgurl")
            #print(r.json().get("imgurl")) # 从二进制数据创建图片对象
        async with httpx.AsyncClient(timeout=20) as client:
            r = requests.get(url, headers=headers)
            with open(path, mode="wb") as f:
                f.write(r.content)  # 使用PIL库保存图片
            return path

if __name__ == '__main__':
    asyncio.run(moyu())
