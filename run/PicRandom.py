# -*- coding:utf-8 -*-
import datetime
import json
import os
import random
import re
import urllib
from asyncio import sleep

import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.tarot import tarotChoice


def main(bot,logger):
    logger.info("抽卡/运势模块启动")
    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData
        if str(event.message_chain) == "meme" or ("meme" in str(event.message_chain) and At(bot.qq) in event.message_chain):
            la = os.listdir("data/pictures/meme")
            la = "data/pictures/meme/" + random.choice(la)
            await bot.send(event, (str(event.sender.member_name) + "得到了一张meme图", Image(path=la)))

    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData
        if ("运势" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="运势":
            la = os.listdir("data/pictures/amm")
            la = "data/pictures/amm/" + random.choice(la)
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


