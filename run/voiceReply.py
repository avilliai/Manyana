# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import time
import sys

import requests
import utils
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate


def main(bot,app_id,app_key,logger):
    logger.info("语音合成用户端启动....")

    models,default,characters=modelLoader()#读取模型

    # modelSelect=['voiceModel/selina/selina.pth','voiceModel/selina/config.json']
    # print('------\n'+str(CHOISE))
    @bot.on(GroupMessage)
    async def characterSpeake(event:GroupMessage):
        if "说" in str(event.message_chain) and str(event.message_chain).split("说")[0] in characters:
            speaker=str(event.message_chain).split("说")[0]
            text = str(event.message_chain).split("说")[1]
            text =await translate(text, app_id, app_key)
            out = '../data/voices/' + random_str() + '.wav'
            logger.info("语音生成_文本" + text)
            logger.info("语音生成_模型:"+speaker + str(characters.get(speaker)[1]))
            data = {"text": "[JA]" + text + "[JA]", "out": out,'speaker':characters.get(speaker)[0],'modelSelect':characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=out[3:]))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "中文" in str(event.message_chain) and str(event.message_chain).split("中文")[0] in characters:
            speaker = str(event.message_chain).split("中文")[0]
            text = str(event.message_chain).split("中文")[1]
            #text = translate(text, app_id, app_key)不用翻译
            out = '../data/voices/' + random_str() + '.wav'
            logger.info("语音生成_文本" + text)
            logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
            data = {"text": "[ZH]" + text + "[ZH]", "out": out, 'speaker': characters.get(speaker)[0],
                    'modelSelect': characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=out[3:]))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "日文" in str(event.message_chain) and str(event.message_chain).split("日文")[0] in characters:
            speaker = str(event.message_chain).split("日文")[0]
            text = str(event.message_chain).split("日文")[1]
            # text = translate(text, app_id, app_key)不用翻译
            logger.info("语音生成_文本"+text)
            out = '../data/voices/' + random_str() + '.wav'
            logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
            data = {"text": "[JA]" + text + "[JA]", "out": out, 'speaker': characters.get(speaker)[0],
                    'modelSelect': characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=out[3:]))




    async def voiceGenerate(data):
        # 将请求参数转换为 JSON 格式
        json_data = json.dumps(data)
        # 向本地 API 发送 POST 请求
        url = 'http://localhost:9080/synthesize'
        response = requests.post(url, json=json_data)
        #print(response.text)

