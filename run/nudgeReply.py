# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import time
import sys

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice, Poke
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import NudgeEvent

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate


def main(bot,master,app_id,app_key,logger):
    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    normal_Reply = result.get("nudgedReply")
    special_Reply = result.get("BeatNudge")
    special_Reply1 = result.get("BeatNudge1")
    voiceReply = result.get("voiceReply")
    chineseVoiceRate=result.get("chineseVoiceRate")
    global modelSelect
    global speaker
    speaker = result.get("defaultModel").get("speaker")
    modelSelect = result.get("defaultModel").get("modelSelect")
    prob=result.get("prob")
    logger.info("读取到apiKey列表")

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
                with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
                    result = yaml.load(f.read(), Loader=yaml.FullLoader)
                defaultModel = result.get("defaultModel")
                defaultModel["speaker"] = speaker
                defaultModel["modelSelect"] = modelSelect
                result["defaultModel"] = defaultModel
                with open('config/nudgeReply.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(result, file, allow_unicode=True)

                await bot.send(event, "成功设置了戳一戳语音生成默认角色为：" + speaker1)
            else:
                await bot.send(event, "不存在的角色")

    @bot.on(NudgeEvent)
    async def NudgeReply(event:NudgeEvent):
        if event.target==bot.qq:
            logger.info("接收到来自" + str(event.from_id) + "的戳一戳")
            if random.randint(0,100)>100-prob:
                await bot.send_group_message(event.subject.id, random.choice(special_Reply))
                try:
                    await bot.send_nudge(target=event.from_id,subject=event.subject.id,kind='Group')
                    await bot.send_group_message(event.subject.id, random.choice(special_Reply1))
                except:
                    try:
                        await bot.send_group_message(event.subject.id,Poke(name="ChuoYiChuo"))
                        await bot.send_group_message(event.subject.id, random.choice(special_Reply1))
                    except:
                        await bot.send_group_message(event.subject.id,"唔....似乎戳不了你呢....好可惜")
            else:
                rep = random.choice(normal_Reply)
                logger.info("回复：" + rep)
                if random.randint(1, 100) > voiceReply:
                    await bot.send_group_message(event.subject.id, rep)
                else:
                    path = '../data/voices/' + random_str() + '.wav'
                    if random.randint(1,100)>chineseVoiceRate:
                        text = await translate(str(rep), app_id, app_key)
                        tex = '[JA]' + text + '[JA]'
                    else:
                        tex="[ZH]"+rep+"[ZH]"
                    logger.info("启动文本转语音：text: " + tex + " path: " + path[3:])
                    await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
                    await bot.send_group_message(event.subject.id, Voice(path=path[3:]))





