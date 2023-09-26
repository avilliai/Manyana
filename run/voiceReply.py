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
from plugins.vitsGenerate import voiceGenerate


def main(bot,master,app_id,app_key,logger):
    logger.info("语音合成用户端启动....")



    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    global modelSelect
    global speaker
    speaker = result.get("defaultModel").get("speaker")
    modelSelect = result.get("defaultModel").get("modelSelect")

    global models
    global characters
    models, default, characters = modelLoader()  # 读取模型

    @bot.on(GroupMessage)
    async def setDefaultModel(event: GroupMessage):
        if event.sender.id == master and str(event.message_chain).startswith("设定角色#"):
            global speaker
            global modelSelect
            if str(event.message_chain).split("#")[1] in characters:
                speaker1 = str(event.message_chain).split("#")[1]
                logger.info("尝试设定角色：" + speaker1)
                speaker = int(characters.get(speaker1)[0])
                modelSelect = characters.get(speaker1)[1]
                logger.info("设置了语音生成_speaker" + str(speaker))
                logger.info("设置了语音生成_模型:" + str(modelSelect))


    # modelSelect=['voiceModel/selina/selina.pth','voiceModel/selina/config.json']
    # print('------\n'+str(CHOISE))
    @bot.on(GroupMessage)
    async def botSaid(event:GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^说\s*(.*)\s*$', msg.strip())
        if m and str(event.message_chain).split("说")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = '../data/voices/' + random_str() + '.wav'
            text = await translate(text, app_id, app_key)
            tex = '[JA]' + text + '[JA]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path[3:]))

    @bot.on(GroupMessage)
    async def botSaid(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^中文\s*(.*)\s*$', msg.strip())
        if m and str(event.message_chain).split("中文")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = '../data/voices/' + random_str() + '.wav'
            #text = await translate(text, app_id, app_key)
            tex = '[ZH]' + text + '[ZH]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path[3:]))

    @bot.on(GroupMessage)
    async def botSaid(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^日文\s*(.*)\s*$', msg.strip())
        if m and str(event.message_chain).split("日文")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = '../data/voices/' + random_str() + '.wav'
            # text = await translate(text, app_id, app_key)
            tex = '[JA]' + text + '[JA]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path[3:]))

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
    @bot.on(GroupMessage)
    async def checkCharacters(event:GroupMessage):
        if "角色" in str(event.message_chain) and At(bot.qq) in event.message_chain:
            str1=""
            for i in characters:
                str1+=i+" |"
            await bot.send(event,"可用角色如下：\n"+str1)



