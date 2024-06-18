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
import zhipuai
from mirai import Image, Voice, Poke
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import NudgeEvent

from concurrent.futures import ThreadPoolExecutor
from plugins.RandomStr import random_str
from plugins.chatGLMonline import glm4
from plugins.gptOfficial import gptOfficial,kimi, qingyan, lingyi, stepAI, qwen, gptvvvv
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, taffySayTest, sovits, edgetts, outVits, modelscopeTTS, superVG
from plugins.yubanGPT import lolimigpt, lolimigpt2
from plugins.googleGemini import geminirep

def main(bot,master,logger,berturl,proxy):
    with open('config.json', 'r', encoding='utf-8') as f:
        datas = yaml.load(f.read(), Loader=yaml.FullLoader)
    configs = datas
    botName = configs.get("botName")
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

    prob=result.get("prob")
    withText=result.get("withText")
    logger.info("读取到apiKey列表")

    global models
    global characters
    try:
        models, default, characters = modelLoader()  # 读取模型
    except:
        logger.error("缺少本地vits模型，无法使用vits模式(非必要)")
        logger.warning("如有需要，请从https://github.com/avilliai/Manyana/releases/download/Manyana/1374_epochsm.pth下载，或在群628763673内获取")
        logger.warning("下载后，将其放置在vits/voiceModel/nene文件夹下")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    speaker92 = result0.get("语音功能设置").get("speaker")
    voiceLangType = str(result0.get("语音功能设置").get("voiceLangType"))
    voicegg=result0.get("语音功能设置").get("voicegenerate")
    chatmodel=result0.get("chatGLM").get("model")
    nudgeornot=result0.get("chatGLM").get("nudgeReply")
    meta1 = result0.get("chatGLM").get("bot_info").get("default")
    gpt3=result0.get("chatGLM").get("bot_info").get("gpt3.5")
    lolimig = result0.get("chatGLM").get("bot_info").get("lolimigpt")
    glm_4=result0.get("chatGLM").get("bot_info").get("glm-4")
    allcharacters = result0.get("chatGLM").get("bot_info")
    Gem=result0.get("chatGLM").get("bot_info").get("Gemini")
    logger.info("语音合成模式："+voicegg+" 语音合成speaker："+speaker92)
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        resulttr = yaml.load(f.read(), Loader=yaml.FullLoader)
    chatGLM_api_key = resulttr.get("chatGLM")
    geminiapikey=resulttr.get("gemini")
    gptkeys=resulttr.get("openai-keys")
    proxy=resulttr.get("proxy")
    os.environ["http_proxy"] = proxy
    if voicegg=="vits":
        with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
            result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
        global modelSelect
        global speaker
        speaker = result2.get("defaultModel").get("speaker")
        modelSelect = result2.get("defaultModel").get("modelSelect")
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

                await bot.send(event, "成功设置了vits语音生成默认角色为：" + speaker1)
            else:
                await bot.send(event, "不存在的vits角色")

    @bot.on(NudgeEvent)
    async def NudgeReply(event:NudgeEvent):
        global transLateData
        if event.target==bot.qq and nudgeornot==False:
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

                    
