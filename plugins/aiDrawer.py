# -*- coding: utf-8 -*-
import asyncio
from io import BytesIO

import httpx

import requests
from PIL import Image

from plugins.RandomStr import random_str


async def draw(prompt,path= "./test.png"):
    url=f"https://api.lolimi.cn/API/AI/sd.php?msg={prompt}&mode=动漫"

    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # print(path)
        return path
async def airedraw(prompt,url,path="./redraw.png"):
    url=f"https://api.lolimi.cn/API/AI/isd.php?msg={prompt}&img={url}&mode=动漫"
    async with httpx.AsyncClient(timeout=40) as client:
        r = await client.get(url)
        img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
        img.save(path)  # 使用PIL库保存图片
        # print(path)
        return path
# 运行 Flask 应用
if __name__ == "__main__":
    asyncio.run(draw("正在吃早饭的二次元少女"))
