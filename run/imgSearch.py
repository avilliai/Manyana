# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import time
import sys
import socket

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str

from plugins.modelsLoader import modelLoader
from plugins.translater import translate



def main(bot,api_key,proxy,logger):
    logger.info("搜图功能启动完毕")
    @bot.on(GroupMessage)
    async def imgSearcher(event:GroupMessage):
        if "搜图" in str(event.message_chain) and event.message_chain.count(Image):
            logger.info("接收来自群："+str(event.group.id)+" 用户："+str(event.sender.id)+" 的搜图指令")
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            proxies = {
                "http://": proxy,
                "https://": proxy
            }

            # Replace the key with your own
            dataa = {"url": img_url, "db": "999", "api_key": api_key, "output_type": "2", "numres": "3"}
            logger.info("发起搜图请求")
            try:
                async with httpx.AsyncClient(proxies=proxies) as client:
                    response = await client.post(url="https://saucenao.com/search.php", data=dataa)
                #response = requests.post(url="https://saucenao.com/search.php", data=dataa, proxies=proxies)
                logger.info("获取到结果"+str(response.json().get("results")[0]))
                #logger.info("下载缩略图")
                #filename=dict_download_img(img_url,dirc="data/pictures/imgSearchCache")
                await bot.send(event,' similarity:'+str(response.json().get("results")[0].get('header').get('similarity'))+"\n"+str(response.json().get("results")[0].get('data')).replace(",","\n").replace("{"," ").replace("}","").replace("'","").replace("[","").replace("]",""),True)
            except:
                logger.warning("搜图失败，无结果或访问次数过多，请稍后再试")
                await bot.send(event,"搜图失败，无结果或访问次数过多，请稍后再试")