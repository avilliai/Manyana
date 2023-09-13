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
from plugins.newsEveryDay import nong
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate
from plugins.webScreenShoot import webScreenShoot, screenshot_to_pdf_and_png


def main(bot,app_id,app_key,logger):
    logger.info("blueArchive")
    global punishing
    with open('data/Punishing.yaml', 'r', encoding='utf-8') as f:
        punishing = yaml.load(f.read(), Loader=yaml.FullLoader)
    global newResult
    with open('data/blueArchive/character.yaml', 'r', encoding='utf-8') as f:
        newResult = yaml.load(f.read(), Loader=yaml.FullLoader)

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        global punishing
        if "战双查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("战双查询")[1]
            logger.info("查询战双角色:" + aimCharacter)
            for i in punishing:
                if aimCharacter in punishing.get(i).get('otherName'):
                    if 'detail' in punishing.get(i):
                        logger.info("存在本地数据文件，直接发送")
                        path = punishing.get(i).get("detail")
                        try:
                            await bot.send(event, Image(path=path))
                            return
                        except:
                            logger.error("失败，重新抓取")

                    if True:
                        logger.warning("没有本地数据文件，启用下载")
                        await bot.send(event,"抓取数据中....初次查询将耗费较长时间。")
                        url = 'https://wiki.biligame.com' + punishing.get(i).get('url')
                        path = "data/pictures/punishing/" + random_str() + '.png'
                        data1 = punishing.get(i)
                        try:
                            #webScreenShoot(url,path,1200,6500)
                            await screenshot_to_pdf_and_png(url, path)
                        except:
                            logger.warning("查询战双角色:" + aimCharacter + " 失败，未收录对应数据")
                            logger.info("发送语音()：数据库里好像没有这个角色呢,要再检查一下吗？")
                            if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                                data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]",
                                        "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                                await voiceGenerate(data)
                                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                            else:
                                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                            return
                        data1["detail"] = path
                        punishing[i] = data1
                        logger.info("写入文件")
                        # logger.info(newResult)
                        with open('data/Punishing.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(punishing, file, allow_unicode=True)

                        logger.info("发送成功")
                        await bot.send(event, Image(path=path))
                    return
                else:
                    continue
            logger.warning("查询战双角色:" + aimCharacter + " 失败，未收录对应数据")
            logger.info("发送语音(日)：数据库里好像没有这个角色呢,要再检查一下吗？")
            if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]", "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                await voiceGenerate(data)
                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
            else:
                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))

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
                        try:
                            await bot.send(event,Image(path=path))
                            return
                        except:
                            logger.error("失败，重新抓取")

                    if True:
                        logger.warning("没有本地数据文件，启用下载")
                        await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                        url='https://blue-utils.me/'+newResult.get(i).get('url')
                        path="data/blueArchive/cache/"+random_str()+'.png'
                        data1=newResult.get(i)
                        try:
                            webScreenShoot(url,path)
                            #await screenshot_to_pdf_and_png(url, path)
                        except:
                            logger.warning("查询ba角色:" + aimCharacter + " 失败，未收录对应数据")
                            logger.info("发送语音()：数据库里好像没有这个角色呢,要再检查一下吗？")
                            if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                                data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]",
                                        "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                                await voiceGenerate(data)
                                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                            else:
                                await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                            return

                        data1["detail"]=path
                        newResult[i]=data1
                        logger.info("写入文件")
                        #logger.info(newResult)
                        with open('data/blueArchive/character.yaml', 'w', encoding="utf-8") as file:
                            yaml.dump(newResult, file, allow_unicode=True)

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

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "明日方舟查询" in str(event.message_chain) or "方舟查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("查询")[1]
            logger.info("查询明日方舟角色:" + aimCharacter)
            cha=os.listdir("data/arknights")
            if aimCharacter+".png" in cha:
                logger.info("存在本地数据文件，直接发送")
                path = "data/arknights/"+aimCharacter+".png"
                try:
                    await bot.send(event, Image(path=path))
                    return
                except:
                    logger.error("失败，重新抓取")

            if True:
                logger.warning("没有本地数据文件，启用下载")
                await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                url = 'https://prts.wiki/w/' + aimCharacter
                path = "data/arknights/"+aimCharacter+".png"

                try:
                    #webScreenShoot(url,path,1200,9500)
                    await screenshot_to_pdf_and_png(url, path,5)
                except:
                    logger.warning("查询方舟角色:" + aimCharacter + " 失败，未收录对应数据")
                    logger.info("发送语音()：数据库里好像没有这个角色呢,要再检查一下吗？")
                    if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                        data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]",
                                "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                        await voiceGenerate(data)
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                    else:
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                        return

                await bot.send(event, Image(path=path))
                logger.info("发送成功")
                return

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "王者查询" in str(event.message_chain) or "农查询" in str(event.message_chain) or "王者荣耀查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("查询")[1]
            logger.info("查询王者荣耀角色:" + aimCharacter)
            cha = os.listdir("data/Elo")
            if aimCharacter + ".png" in cha:
                logger.info("存在本地数据文件，直接发送")
                path = "data/Elo/" + aimCharacter + ".png"
                try:
                    st1=" "
                    try:
                        r = requests.get(
                            url="https://www.sapi.run/hero/select.php?hero=" + aimCharacter + "&type=aqq").json()
                        logger.info("王者战力查询：" + str(r.get("data")).replace(",", "\n"))
                        st1 = str(r.get("data")).replace(",", "\n")
                    except:
                        logger.error("战力查询error")
                    await bot.send(event, (Image(path=path),st1))
                    return
                except:
                    logger.error("失败，重新抓取")

            if True:
                logger.warning("没有本地数据文件，启用下载")
                await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                url = 'https://xiaoapi.cn/API/wzry_pic.php?msg=' + aimCharacter
                path = "data/Elo/" + aimCharacter + ".png"
                st1=" "
                try:
                    # webScreenShoot(url,path,1200,9500)
                    await nong(url,aimCharacter)
                    r=requests.get(url="https://www.sapi.run/hero/select.php?hero="+aimCharacter+"&type=aqq").json()
                    logger.info("王者战力查询："+str(r.get("data")).replace(",", "\n"))
                    st1=str(r.get("data")).replace(",", "\n")
                    #await bot.send(event,str(r.get("data")).replace(",", "\n"))
                except:
                    logger.warning("查询农角色:" + aimCharacter + " 失败，未收录对应数据")
                    logger.info("发送语音()：数据库里好像没有这个角色呢,要再检查一下吗？")
                    if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                        data = {"text": "[ZH]数据库里好像没有这个角色呢,要再检查一下吗？[ZH]",
                                "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                        await voiceGenerate(data)
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                    else:
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                        return

                await bot.send(event, (Image(path=path),st1))
                logger.info("发送成功")
                return

    @bot.on(GroupMessage)
    async def CharacterQuery(event: GroupMessage):
        if "后室查询" in str(event.message_chain) or "br查询" in str(event.message_chain):
            aimCharacter = str(event.message_chain).split("查询")[1]
            logger.info("查询后室层级:" + aimCharacter)
            cha = os.listdir("data/backrooms")
            if aimCharacter + ".png" in cha:
                logger.info("存在本地数据文件，直接发送")
                path = "data/backrooms/" + aimCharacter + ".png"
                try:
                    await bot.send(event, Image(path=path))
                    return
                except:
                    logger.error("失败，重新抓取")

            if True:
                logger.warning("没有本地数据文件，启用下载")
                await bot.send(event, "抓取数据中....初次查询将耗费较长时间。")
                url = 'http://backrooms-wiki-cn.wikidot.com//' + aimCharacter
                path = "data/backrooms/" + aimCharacter + ".png"

                try:
                    # webScreenShoot(url,path,1200,9500)
                    await screenshot_to_pdf_and_png(url, path, 5)
                except:
                    logger.warning("查询后室层级:" + aimCharacter + " 失败，未收录对应数据")
                    logger.info("发送语音()：数据库里好像没有这个层级呢,要再检查一下吗？")
                    if os.path.exists("data/autoReply/voiceReply/queryFalse.wav") == False:
                        data = {"text": "[ZH]数据库里好像没有这个层级呢,要再检查一下吗？[ZH]",
                                "out": "../data/autoReply/voiceReply/queryFalse.wav"}
                        await voiceGenerate(data)
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                    else:
                        await bot.send(event, Voice(path="data/autoReply/voiceReply/queryFalse.wav"))
                        return

                await bot.send(event, Image(path=path))
                logger.info("发送成功")
                return