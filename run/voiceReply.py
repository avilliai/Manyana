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

from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, superVG, fetch_FishTTS_ModelId


def main(bot,master,logger):
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    FishTTSAuthorization=result0.get("FishTTSAuthorization")
    proxy=result0.get("proxy")


    with open('config/autoSettings.yaml', 'r', encoding='utf-8') as f:
        result2 = yaml.load(f.read(), Loader=yaml.FullLoader)
    global modelSelect
    global speaker
    speaker = result2.get("defaultModel").get("speaker")
    modelSelect = result2.get("defaultModel").get("modelSelect")

    global models
    global characters
    try:
        from plugins.modelsLoader import modelLoader
        models, default, characters = modelLoader()  # 读取模型
    except Exception as e:
        characters={"None":"无可用模型"}

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
    async def botSaid(event: GroupMessage):
        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^中文\s*(.*)\s*$', msg.strip())

        if m and str(event.message_chain).split("中文")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = 'data/voices/' + random_str() + '.wav'

            tex = '[ZH]' + text + '[ZH]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path)
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def botSaid(event: GroupMessage):

        msg = "".join(map(str, event.message_chain[Plain]))
        # 匹配指令
        m = re.match(r'^日文\s*(.*)\s*$', msg.strip())
        if m and str(event.message_chain).split("日文")[0] not in characters and At(bot.qq) in event.message_chain:
            # 取出指令中的地名
            text = m.group(1)
            path = 'data/voices/' + random_str() + '.wav'

            tex = '[JA]' + text + '[JA]'
            logger.info("启动文本转语音：text: " + tex + " path: " + path)
            await voiceGenerate({"text": tex, "out": path,"speaker":speaker,"modelSelect":modelSelect})
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event:GroupMessage):
        if "说" in str(event.message_chain) and str(event.message_chain).startswith("说")==False:

            text = str(event.message_chain)[len(str(event.message_chain).split("说")[0])+1:]
            if str(event.message_chain).split("说")[0] in characters:
                speaker = str(event.message_chain).split("说")[0]
                text =await translate(text)
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_文本" + text)
                logger.info("语音生成_模型:"+speaker + str(characters.get(speaker)[1]))
                data = {"text": "[JA]" + text + "[JA]", "out": path,'speaker':characters.get(speaker)[0],'modelSelect':characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))
            try:
                sp1=await fetch_FishTTS_ModelId(proxy,FishTTSAuthorization,str(event.message_chain).split("说")[0])
                if sp1==None or sp1=="":
                    logger.warning("未能在FishTTS中找到对应角色")
                    return
                else:
                    logger.info(f"获取到FishTTS模型id {str(event.message_chain).split('说')[0]} {sp1}")
                    p=await superVG({"text":str(event.message_chain).split("说")[1],"speaker":sp1},"FishTTS")
                    await bot.send(event, Voice(path=p))
            except Exception as e:
                logger.error(e)

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "中文" in str(event.message_chain) and str(event.message_chain).split("中文")[0] in characters:
            speaker = str(event.message_chain).split("中文")[0]
            text = str(event.message_chain).split("中文")[1]

            path = 'data/voices/' + random_str() + '.wav'
            logger.info("语音生成_文本" + text)
            logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
            data = {"text": "[ZH]" + text + "[ZH]", "out": path, 'speaker': characters.get(speaker)[0],
                    'modelSelect': characters.get(speaker)[1]}
            await voiceGenerate(data)
            await bot.send(event, Voice(path=path))

    @bot.on(GroupMessage)
    async def characterSpeake(event: GroupMessage):
        if "日文" in str(event.message_chain):
            speaker = str(event.message_chain).split("日文")[0]
            text = str(event.message_chain)[len(str(event.message_chain).split("日文")[0])+1:]

            logger.info("语音生成_文本"+text)
            if str(event.message_chain).split("日文")[0] in characters:
                path = 'data/voices/' + random_str() + '.wav'
                logger.info("语音生成_模型:" + speaker + str(characters.get(speaker)[1]))
                data = {"text": "[JA]" + text + "[JA]", "out": path, 'speaker': characters.get(speaker)[0],
                        'modelSelect': characters.get(speaker)[1]}
                await voiceGenerate(data)
                await bot.send(event, Voice(path=path))
            try:
                sp1 = await fetch_FishTTS_ModelId(proxy, FishTTSAuthorization, str(event.message_chain).split("日文")[0])
                if sp1 == None or sp1 == "":
                    logger.warning("未能在FishTTS中找到对应角色")
                    return
                else:
                    logger.info(f"获取到FishTTS模型id {str(event.message_chain).split('日文')[0]} {sp1}")
                    p = await superVG(data={"text": text, "speaker": sp1}, mode="FishTTS",langmode="<jp>")
                    await bot.send(event, Voice(path=p))
            except Exception as e:
                logger.error(e)
    @bot.on(GroupMessage)
    async def checkCharacters(event:GroupMessage):
        if "角色" in str(event.message_chain) and At(bot.qq) in event.message_chain and "模板" not in str(event.message_chain):

            str1="vits可用角色如下：\n"
            for i in characters:
                str1+=i+" |"
            str1+="\n\nbert_vits2可用角色如下：\n"+str(["BT","塔菲","阿梓","otto","丁真","星瞳","东雪莲","嘉然","孙笑川","亚托克斯","文静","鹿鸣","奶绿","七海","恬豆","科比"])+"\n\nFishTTS可用角色请查看https://fish.audio/zh-CN/，均可通过 xx说调用。\n"
            #print(str1)
            #await bot.send(event, [str1,Image(path="data/fonts/图片-1717384652980.png")])
            #await bot.send(event,Image(path="data/fonts/fireflyspeakers.jpg"))
            await bot.send(event,"可发送 xx说.......  以进行语音合成")



