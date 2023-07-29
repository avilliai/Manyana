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
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate
from plugins.webScreenShoot import webScreenShoot


def main(bot,app_id,app_key,logger):
    logger.info("blueArchive")
    with open('data/blueArchive/characterName.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    global newResult
    with open('data/blueArchive/character.yaml', 'r', encoding='utf-8') as f:
        newResult = yaml.load(f.read(), Loader=yaml.FullLoader)


    @bot.on(GroupMessage)
    async def CharacterQuery(event:GroupMessage):
        global newResult
        if "ba查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("ba查询")[1]
            logger.info("查询ba角色:" + aimCharacter)
            for i in newResult:
                if aimCharacter in newResult.get(i).get('otherName'):
                    if 'detail' in newResult.get(i):
                        logger.info("存在本地数据文件，直接发送")
                        path=newResult.get(i).get("detail")
                        await bot.send(event,Image(path=path))
                    else:
                        logger.warning("没有本地数据文件，启用下载")
                        url='https://blue-utils.me/'+newResult.get(i).get('url')
                        path="data/blueArchive/cache/"+random_str()+'.png'
                        data1=newResult.get(i)

                        data1["detail"]=path
                        newResult[i]=data1
                        logger.info("写入文件")
                        #logger.info(newResult)
                        with open('data/blueArchive/character.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(data1, file, allow_unicode=True)
                        webScreenShoot(url,path)
                        logger.info("发送成功")
                        await bot.send(event,Image(path=path))
                    return
                else:
                    continue
            logger.warning("查询ba角色:" + aimCharacter + " 失败，未收录对应数据")
            logger.info("发送语音(日)：数据库里好像没有这个角色呢,要再检查一下吗？")
            if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]", "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                await voiceGenerate(data)
                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
            else:
                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))

            '''url=""
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
                    back=await translate("数据库里好像没有这个角色呢,要再检查一下吗？",app_id,app_key)
                    data={"text":"[JA]"+str(back)+"[JA]","out":"../data/autoReply/voiceReply/queryFalse.wav"}
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
                profile=await translate(data1.get("profile").replace("\n",""),app_id,app_key,aim="zh-CHS",ori="ja")
                logger.info("获取profile翻译结果："+str(profile))
                data1["profile"]=profile

                try:
                    await bot.send(event,(Image(path=icon),str(data1).replace(",","\n").replace("armorType","装甲类型").replace("baseStar","初始星级").replace("bulletType","攻击类型").replace("position","位置").replace("name","名字").replace("profile","简介").replace("rarity","稀有度").replace("role","职业").replace('squadType',"小队类型").replace("weaponType","武器类型")))
                    await bot.send(event, (Image(path=lobby),str(response.get("info")).replace(",", "\n")))
                    await bot.send(event,Image(path=portrait))
                except:
                    await bot.send(event, str(data1).replace(",", "\n").replace("armorType", "装甲类型").replace("baseStar", "初始星级").replace("bulletType", "攻击类型").replace("position","位置").replace("name", "名字").replace("profile", "简介").replace("rarity", "稀有度").replace("role", "职业").replace('squadType', "小队类型").replace("weaponType","武器类型"))
                    await bot.send(event,str(response.get("info")).replace(",", "\n"))

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "ba技能查询" in str(event.message_chain):
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
                    da=await translate("数据库里好像没有这个角色呢,要再检查一下吗？", app_id, app_key)
                    data = {"text": "[JA]" + str(da) + "[JA]",
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

                try:
                    await bot.send(event, (Image(path=icon),str(data1).replace(",", "\n")))
                    await bot.send(event, (Image(path=lobby), str(response.get("terrain")).replace(",", "\n").replace("'urban'"," 市区").replace("'outdoor'","室外").replace("'indoor'","室内").replace("'DamageDealt'","伤害").replace("'ShieldBlockRate'","掩体成功率").replace("{","").replace("}","")))
                except:
                    await bot.send(event, str(data1).replace(",", "\n"))
                    await bot.send(event, str(response.get("terrain")).replace(",", "\n").replace("'urban'"," 市区").replace("'outdoor'", "室外").replace("'indoor'", "室内").replace("'DamageDealt'","伤害").replace("'ShieldBlockRate'", "掩体成功率").replace("{", "").replace("}", ""))'''




