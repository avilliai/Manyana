# -*- coding:utf-8 -*-
import datetime
import json
import os
import random
import re
import urllib
from asyncio import sleep
from io import BytesIO

import httpx
import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.tarot import tarotChoice
from PIL import Image as Image1

def main(bot,proxy,logger):
    logger.info("抽卡/运势模块启动")
    colorfulCharacterList = os.listdir("data/colorfulAnimeCharacter")
    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData
        if str(event.message_chain) == "meme" or ("meme" in str(event.message_chain) and At(bot.qq) in event.message_chain):
            try:
                logger.info("使用网络meme")

                url = 'https://meme-api.com/gimme'
                proxies = {
                    "http://": proxy,
                    "https://": proxy
                }
                async with httpx.AsyncClient(timeout=20) as client:
                    r = await client.get(url)
                    logger.info(r.json().get("preview")[-1])
                    async with httpx.AsyncClient(timeout=20, proxies=proxies) as client:
                        r = await client.get(r.json().get("preview")[-1])
                        img = Image1.open(BytesIO(r.content))  # 从二进制数据创建图片对象
                        path = "data/pictures/meme/" + random_str() + ".png"
                        img.save(path)  # 使用PIL库保存图片
                        await bot.send(event, Image(path=path))

            except:
                logger.warning("网络meme出错，使用本地meme图")
                la = os.listdir("data/pictures/meme")
                la = "data/pictures/meme/" + random.choice(la)
                logger.info("掉落了一张meme图")
                await bot.send(event, (str(event.sender.member_name) + "得到了一张meme图", Image(path=la)))

    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData
        if ("运势" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="运势":
            la = os.listdir("data/pictures/amm")
            la = "data/pictures/amm/" + random.choice(la)
            logger.info("执行运势查询")
            await bot.send(event, (str(event.sender.member_name) + "今天的运势是", Image(path=la)))

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        if ("今日塔罗" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "今日塔罗":
            logger.info("获取今日塔罗")
            txt, img = tarotChoice()
            logger.info("成功获取到今日塔罗")
            await bot.send(event, txt)
            await bot.send(event, Image(path=img))

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        if ("彩色小人" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(
                event.message_chain) == "彩色小人":
            logger.info("彩色小人，启动！")
            c = random.choice(colorfulCharacterList)
            await bot.send(event, Image(path="data/colorfulAnimeCharacter/" + c))



