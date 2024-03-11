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
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import taffySayTest, superVG


def main(bot,logger,berturl,proxy):
    logger.info("bert_vits语音合成用户端启动....")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    spe=result.get("bert_speakers")
    modelScope=["塔菲","阿梓","otto","丁真","星瞳","东雪莲","嘉然","孙笑川","亚托克斯","文静","鹿鸣"]
    @bot.on(GroupMessage)
    async def taffySayf(event:GroupMessage):

        if "说" in str(event.message_chain) and str(event.message_chain).split("说")[0] in spe:
            data={}

            data["speaker"]=str(event.message_chain).split("说")[0]
            data["text"]=str(event.message_chain).replace(str(event.message_chain).split("说")[0]+"说","")
            try:
                path=await taffySayTest(data,berturl,proxy)
                await bot.send(event,Voice(path=path))
            except:
                pass

    @bot.on(GroupMessage)
    async def taffySays(event:GroupMessage):
        if "说" in str(event.message_chain) and str(event.message_chain).split("说")[0] in modelScope:
            try:
                data = {}
                data["speaker"] = str(event.message_chain).split("说")[0]
                data["text"] = str(event.message_chain).replace(str(event.message_chain).split("说")[0] + "说", "")
                logger.info("modelscopeTTS语音合成:"+data["text"])
                path=await superVG(data,"modelscopeTTS")
                await bot.send(event,Voice(path=path))
            except Exception as e:
                logger.error(e)