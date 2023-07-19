# -*- coding: utf-8 -*-
import os

import httpx
import asyncio

import requests

from plugins.RandomStr import random_str


'''async def pic():

    url = "https://iw233.cn/api.php?sort=random"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
        "Referer": "https://weibo.com/"}
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        r = r.content
        ranpath=random_str()
        path="../data/pictures/wallpaper/" + ranpath + ".png"
        with open(path, mode="wb") as f:
            f.write(r)  # 图片内容写入文件
        return path'''


def pic():
    url = "https://iw233.cn/api.php?sort=random"
    # url+="tag=萝莉|少女&tag=白丝|黑丝"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54",
        "Referer": "https://weibo.com/"}
    r = requests.get(url, headers=headers).content

    ranpath = random_str()

    with open("data/pictures/wallpaper/" + ranpath + ".png", mode="wb") as f:
        f.write(r)  # 图片内容写入文件
    return "data/pictures/wallpaper/" + ranpath + ".png"
if __name__ == '__main__':
    #asyncio.run(pic())
    pic()