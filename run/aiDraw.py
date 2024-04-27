# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.aiDrawer import draw, airedraw, draw1, draw3


def main(bot,logger):
    logger.info("ai绘画 启用")
    global redraw
    redraw={}
    @bot.on(GroupMessage)
    async def aidrawf(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag=str(event.message_chain).replace("画 ","")
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("发起ai绘画请求，path:"+path+"|prompt:"+tag)
            i=1
            while i<10:
                logger.info(f"接口1第{i}次请求")
                try:
                    logger.info("接口1绘画中......")
                    p=await draw1(tag,path)
                    await bot.send(event,Image(path=p),True)
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error("接口1绘画失败.......")
                    #await bot.send(event,"接口1绘画失败.......")
                i+=1
            if i>10:
                await bot.send(event, "接口绘画失败.......")
    @bot.on(GroupMessage)
    async def aidrawff(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag=str(event.message_chain).replace("画 ","")
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("发起ai绘画请求，path:"+path+"|prompt:"+tag)
            i=1
            while i<10:
                logger.info(f"接口2第{i}次请求")
                try:
                    logger.info("接口2绘画中......")
                    p=await draw(tag,path)
                    await bot.send(event,Image(path=p),True)
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error("接口2绘画失败.......")
                    #await bot.send(event,"接口2绘画失败.......")
                i+=1
            if i>10:
                await bot.send(event, "接口绘画失败.......")

    @bot.on(GroupMessage)
    async def aidrawff(event: GroupMessage):
        if str(event.message_chain).startswith("画 "):
            tag = str(event.message_chain).replace("画 ", "")
            path = "data/pictures/cache/" + random_str() + ".png"
            logger.info("发起ai绘画请求，path:" + path + "|prompt:" + tag)
            i = 1
            while i < 10:
                logger.info(f"接口3第{i}次请求")
                try:
                    logger.info("接口3绘画中......")
                    p = await draw3(tag, path)
                    await bot.send(event, Image(path=p), True)
                    break
                except Exception as e:
                    logger.error(e)
                    logger.error("接口3绘画失败.......")
                    # await bot.send(event,"接口2绘画失败.......")
                i += 1
            if i > 10:
                await bot.send(event, "接口绘画失败.......")
    @bot.on(GroupMessage)
    async def rededd(event: GroupMessage):
        global redraw
        if str(event.message_chain).startswith("以图生图 "):
            await bot.send(event,"请发送图片，bot随后将开始绘制")
            redraw[event.sender.id]=str(event.message_chain).replace("以图生图 ","")
    @bot.on(GroupMessage)
    async def redrawStart(event: GroupMessage):
        global redraw
        if event.message_chain.count(Image) and event.sender.id in redraw:
            prompt=redraw.get(event.sender.id)
            lst_img = event.message_chain.get(Image)
            url1 = lst_img[0].url
            logger.info(f"以图生图,prompt:{prompt} url:{url1}")
            try:
                p=await airedraw(prompt,url1)
                await bot.send(event,Image(path=p))
                redraw.pop(event.sender.id)
            except Exception as e:
                logger.error(e)
                logger.error("ai绘画出错")
                await bot.send(event,"ai绘画出错")
                redraw.pop(event.sender.id)
