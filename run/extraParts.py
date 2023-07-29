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
from plugins.arkOperator import arkOperator
from plugins.cpGenerate import get_cp_mesg
from plugins.genshinGo import genshinDraw
from plugins.historicalToday import hisToday
from plugins.imgDownload import dict_download_img
from plugins.jokeMaker import get_joke

from plugins.modelsLoader import modelLoader
from plugins.newsEveryDay import news, moyu
from plugins.picGet import pic, setuGet
from plugins.tarot import tarotChoice
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate


def main(bot,api_KEY,app_id,app_key,nasa_api,proxy,logger):
    logger.info("额外的功能 启动完成")
    with open("data/odes.json",encoding="utf-8") as fp:
        odes=json.loads(fp.read())
    with open("data/IChing.json",encoding="utf-8") as fp:
        IChing=json.loads(fp.read())


    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        # if str(event.message_chain) == '/pic':
        if At(bot.qq) not in event.message_chain:
            if '/pic' in str(event.message_chain):
                picNum = int((str(event.message_chain))[4:])
            elif "@"+str(bot.qq) not in str(event.message_chain) and event.message_chain.count(Image)<1 and len(str(event.message_chain))<6:
                if get_number(str(event.message_chain))==None:
                    return
                else:
                    picNum=int(get_number(str(event.message_chain)))

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
    async def setuHelper(event:GroupMessage):
        pattern1 = r'(\d+)张(\w+)'
        if At(bot.qq) in event.message_chain:
            text1=str(event.message_chain).replace("壁纸","").replace("涩图","").replace("色图","").replace("图","").replace("r18","")
            match1 = re.search(pattern1, text1)
            if match1:
                logger.info("提取图片关键字。 数量: "+str(match1.group(1))+" 关键字: "+match1.group(2))
                data={"tag":""}
                if "r18" in str(event.message_chain) or "色图" in str(event.message_chain) or "涩图" in str(event.message_chain):
                    data["tag"]=match1.group(2)
                    data["r18"]=1
                else:
                    data["tag"]=match1.group(2)
                logger.info("组装数据完成："+str(data))
                for i in range(int(match1.group(1))):
                    path=await setuGet(data)
                    logger.info("发送图片: "+path)
                    await bot.send(event,Image(path=path))
                    logger.info("图片发送成功")

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
    async def make_jokes(event: GroupMessage):
        if str(event.message_chain).startswith('/') and str(event.message_chain).endswith('笑话'):
            x = str(event.message_chain).strip()[1:-2]
            joke = get_joke(x)
            await bot.send(event, joke)

    # 凑个cp
    @bot.on(GroupMessage)
    async def make_cp_mesg(event: GroupMessage):
        if str(event.message_chain).startswith("/cp "):
            x = str(event.message_chain).replace('/cp ', '', 1)
            x = x.split(' ')
            if len(x) != 2:
                path = '../data/voices/' + random_str() + '.wav'
                text='エラーが発生しました。再入力してください'
                tex = '[JA]' + text + '[JA]'
                logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
                await voiceGenerate({"text": tex, "out": path})
                await bot.send(event, Voice(path=path))
                return
            mesg = get_cp_mesg(x[0], x[1])
            await bot.send(event, mesg, True)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "天文" in str(event.message_chain):
            proxies = {
                "http://": proxy,
                "https://": proxy
            }
            # Replace the key with your own
            dataa = {"api_key": nasa_api}
            logger.info("发起nasa请求")
            try:
                # 拼接url和参数
                url = "https://api.nasa.gov/planetary/apod?" + "&".join([f"{k}={v}" for k, v in dataa.items()])
                async with httpx.AsyncClient(proxies=proxies) as client:
                    # 用get方法发送请求
                    response = await client.get(url=url)
                # response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                logger.info("获取到结果" + str(response.json()))
                # logger.info("下载缩略图")
                filename = dict_download_img(response.json().get("url"), dirc="data/pictures/cache")
                txta=await translate(response.json().get("explanation"),app_id=app_id,app_key=app_key,ori="en",aim="zh-CHS")
                txt = response.json().get("date") + "\n" + response.json().get("title") + "\n" + txta
                await bot.send(event,(Image(path=filename),txt))

            except:
                logger.warning("获取每日天文图片失败")
                await bot.send(event,"获取失败，请联系master检查代理或api_key是否可用")
    @bot.on(GroupMessage)
    async def arkGene(event:GroupMessage):
        if "干员" in str(event.message_chain) and "生成" in str(event.message_chain):
            logger.info("又有皱皮了，生成干员信息中.....")
            o=arkOperator()
            o=o.replace("为生成",event.sender.member_name)
            await bot.send(event,o,True)

    @bot.on(GroupMessage)
    async def genshin1(event: GroupMessage):
        if ("原神" in str(event.message_chain) and "启动" in str(event.message_chain)) or ("抽签" in str(event.message_chain) and "原" in str(event.message_chain)):
            logger.info("有原皮！获取抽签信息中....")
            o = genshinDraw()
            logger.info("\n"+o)
            await bot.send(event, o, True)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "诗经" in str(event.message_chain):
            logger.info("获取一篇诗经")
            ode=random.choice(odes.get("诗经"))
            logger.info("\n"+ode)
            await bot.send(event,ode)

    @bot.on(GroupMessage)
    async def NasaHelper(event: GroupMessage):
        if At(bot.qq) in event.message_chain and "周易" in str(event.message_chain):
            logger.info("获取卦象")
            ode = random.choice(odes.get("六十四卦"))
            logger.info("\n" + ode)
            await bot.send(event, ode)

