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
from mirai import Image, Voice, Poke
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import NudgeEvent

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, taffySayTest, sovits, edgetts


def main(bot,master,app_id,app_key,logger,berturl,proxy):
    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    normal_Reply = result.get("nudgedReply")
    special_Reply = result.get("BeatNudge")
    special_Reply1 = result.get("BeatNudge1")
    voiceReply = result.get("voiceReply")
    chineseVoiceRate=result.get("chineseVoiceRate")
    bert_vits2_mode=result.get("bert_vits2_mode")
    global transLateData
    with open('data/autoReply/transLateData.yaml', 'r', encoding='utf-8') as file:
        transLateData = yaml.load(file, Loader=yaml.FullLoader)
    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global modelSelect
    global speaker
    speaker = result2.get("defaultModel").get("speaker")
    modelSelect = result2.get("defaultModel").get("modelSelect")
    prob=result.get("prob")
    withText=result.get("withText")
    logger.info("读取到apiKey列表")

    global models
    global characters
    models, default, characters = modelLoader()  # 读取模型
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    speaker92 = result0.get("chatGLM").get("speaker")
    voicegg=result0.get("voicegenerate")
    logger.info("语音合成模式："+voicegg+" 语音合成speaker："+speaker92)
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
                with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
                    result = yaml.load(f.read(), Loader=yaml.FullLoader)
                defaultModel = result.get("defaultModel")
                defaultModel["speaker"] = speaker
                defaultModel["modelSelect"] = modelSelect
                result["defaultModel"] = defaultModel
                with open('config/autoSettings.yaml', 'w', encoding="utf-8") as file:
                    yaml.dump(result, file, allow_unicode=True)

                await bot.send(event, "成功设置了戳一戳语音生成默认角色为：" + speaker1)
            else:
                await bot.send(event, "不存在的角色")

    @bot.on(NudgeEvent)
    async def NudgeReply(event:NudgeEvent):
        global transLateData
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
                    daf={}
                    daf["speaker"]=speaker92
                    st8 = re.sub(r"（[^）]*）", "", rep)
                    daf["text"]=st8

                    # print(path)
                      # 使用r前缀表示原始字符串，避免转义字符的问题
                    try:
                        if voicegg=="bert_vits2":
                            logger.info("调用bert_vits语音回复")
                            path = await taffySayTest(daf, berturl, proxy)
                            await bot.send_group_message(event.subject.id, Voice(path=path))
                            if withText == True:
                                await bot.send_group_message(event.subject.id,  rep)
                        elif voicegg=="so-vits":
                            logger.info("调用so-vits语音回复")
                            r = await sovits({"text": st8, "speaker": "riri"})
                            logger.info("tts 完成")
                            await bot.send(event, Voice(path=r))
                            if withText == True:
                                await bot.send_group_message(event.subject.id, rep)
                        elif voicegg=="edgetts":
                            r = await edgetts({"text": st8, "speaker": speaker92})
                            logger.info("edgetts 完成")
                            await bot.send(event, Voice(path=r))
                            if withText == True:
                                await bot.send_group_message(event.subject.id, rep)
                    except:
                        logger.error("bert_vits2语音合成服务已关闭，改用vits合成语音")
                        path = 'data/voices/' + random_str() + '.wav'
                        if random.randint(1, 100) > chineseVoiceRate:
                            if rep in transLateData:
                                text = transLateData.get(rep)
                            else:
                                text = await translate(str(rep), app_id, app_key)
                                transLateData[rep] = text
                                with open('data/autoReply/transLateData.yaml', 'w', encoding="utf-8") as file:
                                    yaml.dump(transLateData, file, allow_unicode=True)
                                logger.info("写入参照数据:" + rep + "| " + text)
                            tex = '[JA]' + text + '[JA]'
                        else:
                            tex = "[ZH]" + rep + "[ZH]"
                        logger.info("启动文本转语音：text: " + tex + " path: " + path)
                        await voiceGenerate(
                            {"text": tex, "out": path, "speaker": speaker, "modelSelect": modelSelect})
                        await bot.send_group_message(event.subject.id, Voice(path=path))

                            #await bot.send_group_message(event.subject.id,  rep)





