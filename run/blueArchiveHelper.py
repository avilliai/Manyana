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
import yaml
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate



def main(bot,app_id,app_key,logger):
    logger.info("blueArchive")
    with open('data/blueArchive/characterName.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)

    @bot.on(GroupMessage)
    async def CharacterQuery(event:GroupMessage):
        if str(event.message_chain).startswith("ba查询"):
            url=""
            aimCharacter=str(event.message_chain).split("ba查询")[1]
            if aimCharacter in result:
                url = 'https://api.ennead.cc/buruaka/character/' + aimCharacter + '?region=japan'  # 指定角色信息

            else:
                for i in result:
                    for s in result.get(i):
                        if s==aimCharacter:
                            url='https://api.ennead.cc/buruaka/character/'+i+'?region=japan'  # 指定角色信息
                            break
            if url=="":
                logger.warning("查询ba角色:"+aimCharacter+" 失败，未收录对应数据")
                logger.info("发送语音(日)：数据库里好像没有这个角色呢,要再检查一下吗？")
                if os.path.exists("data/autoReply/voiceReply/queryFalse.wav")==False:
                    data={"text":"[JA]"+translate("数据库里好像没有这个角色呢,要再检查一下吗？",app_id,app_key)+"[JA]","out":"../data/autoReply/voiceReply/queryFalse.wav"}
                    await voiceGenerate(data)
                    await bot.send(event,Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                else:
                    await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
            else:
                logger.info("查询ba角色:"+aimCharacter)
                response = requests.get(url).json()
                #print(response,type(response))
                logger.info("正在发起请求.....")
                imgData = response.get("image")
                icon = imgData.get("icon").replace("https://api.ennead.cc/buruaka", "data/blueArchive/") + ".png"
                lobby = imgData.get("lobby").replace("https://api.ennead.cc/buruaka", "data/blueArchive/") + ".png"
                portrait = imgData.get("portrait").replace("https://api.ennead.cc/buruaka",
                                                           "data/blueArchive/") + ".png"
                data1=response.get("character")
                profile=translate(data1.get("profile").replace("\n",""),app_id,app_key,aim="zh-CHS",ori="ja")
                logger.info("获取profile翻译结果："+profile)
                data1["profile"]=profile


                await bot.send(event,(Image(path=icon),str(data1).replace(",","\n").replace("armorType","装甲类型").replace("baseStar","初始星级").replace("bulletType","攻击类型").replace("position","位置").replace("name","名字").replace("profile","简介").replace("rarity","稀有度").replace("role","职业").replace('squadType',"小队类型").replace("weaponType","武器类型")))
                await bot.send(event, (Image(path=lobby),str(response.get("info")).replace(",", "\n")))
                await bot.send(event,Image(path=portrait))

        @bot.on(GroupMessage)
        async def CharacterQuery(event: GroupMessage):
            if str(event.message_chain).startswith("ba技能查询"):
                url = ""
                aimCharacter = str(event.message_chain).split("ba技能查询")[1]
                if aimCharacter in result:
                    url = 'https://api.ennead.cc/buruaka/character/' + aimCharacter + '?region=japan'  # 指定角色信息

                else:
                    for i in result:
                        for s in result.get(i):
                            if s == aimCharacter:
                                url = 'https://api.ennead.cc/buruaka/character/' + i + '?region=japan'  # 指定角色信息
                                break
                if url == "":
                    logger.warning("查询ba角色技能:" + aimCharacter + " 失败，未收录对应数据")
                    logger.info("发送语音(日)：数据库里好像没有这个角色呢,要再检查一下吗？")
                    if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                        data = {"text": "[JA]" + translate("数据库里好像没有这个角色呢,要再检查一下吗？", app_id, app_key) + "[JA]",
                                "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                        await voiceGenerate(data)
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                    else:
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                else:
                    logger.info("查询ba角色技能:" + aimCharacter)
                    response = requests.get(url).json()
                    # print(response,type(response))
                    imgData = response.get("image")
                    icon = imgData.get("icon").replace("https://api.ennead.cc/buruaka", "data/blueArchive/") + ".png"
                    lobby = imgData.get("lobby").replace("https://api.ennead.cc/buruaka", "data/blueArchive/") + ".png"
                    portrait = imgData.get("portrait").replace("https://api.ennead.cc/buruaka",
                                                               "data/blueArchive/") + ".png"
                    data1 = response.get("stat")


                    await bot.send(event, (Image(path=icon),
                                           str(data1).replace(",", "\n")))
                    await bot.send(event, (Image(path=lobby), str(response.get("terrain")).replace(",", "\n")))


    async def voiceGenerate(data):
        # 将请求参数转换为 JSON 格式
        json_data = json.dumps(data)
        # 向本地 API 发送 POST 请求
        url = 'http://localhost:9080/synthesize'
        response = requests.post(url, json=json_data)
        #print(response.text)



