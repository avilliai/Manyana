# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys
import socket

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins import weatherQuery
from plugins.RandomStr import random_str
from plugins.historicalToday import hisToday

from plugins.modelsLoader import modelLoader
from plugins.newsEveryDay import news, moyu
from plugins.picGet import pic
from plugins.tarot import tarotChoice
from plugins.translater import translate



def main(bot,api_KEY,logger):
    logger.info("额外的功能 启动完成")

    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        # if str(event.message_chain) == '/pic':

        if '/pic' in str(event.message_chain):
            picNum = int((str(event.message_chain))[4:])
        elif "@"+str(bot.qq) in str(event.message_chain):
            if get_number(str(event.message_chain).replace("@"+str(bot.qq),""))==None:
                return
            else:
                picNum=int(get_number(str(event.message_chain).replace("@"+str(bot.qq),"")))

        else:
            return
        logger.info("图片获取指令....数量："+str(picNum))
        if picNum < 10 and picNum > -1:
            for i in range(picNum):
                logger.info("获取壁纸")
                a = pic()
                await bot.send(event, Image(path=a))
        elif picNum == '':
            a = pic()
            await bot.send(event, Image(path=a))
        else:
            await bot.send(event, "数字超出限制")
        logger.info("图片获取完成")

    # 整点正则
    pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"

    # 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
    def get_number(string):
        # 使用re.match方法，返回匹配的结果对象
        match = re.match(pattern, string)
        # 如果结果对象不为空，返回捕获的数字，否则返回None
        if match:
            # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
            if match.group(2):
                return match.group(2)
            else:
                return match.group(3)
        else:
            return None
    @bot.on(GroupMessage)
    async def historyToday(event:GroupMessage):
        pattern = r".*史.*今.*|.*今.*史.*"
        string = str(event.message_chain)
        match = re.search(pattern, string)
        if match:
            dataBack=await hisToday()
            logger.info("获取历史上的今天")
            logger.info(str(dataBack))
            sendData=str(dataBack.get("result")).replace("["," ").replace("{'year': '","").replace("'}","").replace("]","").replace("', 'title': '"," ").replace(",","\n")
            await bot.send(event,sendData)

    @bot.on(GroupMessage)
    async def weather_query(event: GroupMessage):
        # 从消息链中取出文本
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^查询\s*(\w+)\s*$', msg.strip())
        if m:
            # 取出指令中的地名
            city = m.group(1)
            logger.info("查询 "+city+" 天气")
            await bot.send(event, '查询中……')
            # 发送天气消息
            await bot.send(event, await weatherQuery.querys(city,api_KEY))
    @bot.on(GroupMessage)
    async def newsToday(event:GroupMessage):
        if ("新闻" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="新闻":
            logger.info("获取新闻")
            path=await news()
            logger.info("成功获取到今日新闻")
            await bot.send(event,Image(path=path))

    @bot.on(GroupMessage)
    async def moyuToday(event: GroupMessage):
        if ("摸鱼" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="摸鱼":
            logger.info("获取摸鱼人日历")
            path = await moyu()
            logger.info("成功获取到摸鱼人日历")
            await bot.send(event, Image(path=path))

    @bot.on(GroupMessage)
    async def tarotToday(event: GroupMessage):
        if ("今日塔罗" in str(event.message_chain) and At(bot.qq) in event.message_chain) or str(event.message_chain)=="今日塔罗":
            logger.info("获取今日塔罗")
            txt,img = tarotChoice()
            logger.info("成功获取到今日塔罗")
            await bot.send(event,txt)
            await bot.send(event, Image(path=img))

    async def voiceGenerate(data):
        # 向本地 API 发送 POST 请求
        url = 'http://localhost:9080/synthesize'
        data = json.dumps(data)
        async with httpx.AsyncClient(timeout=None) as client:
            await client.post(url, json=data)
        logger.info("语音生成完成")