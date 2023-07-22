# -*- coding:utf-8 -*-
import asyncio
import datetime
import json

import os
import subprocess
from asyncio import sleep
from random import random

import httpx
import requests
import yaml
from mirai import Mirai, FriendMessage, WebSocketAdapter, Poke, GroupMessage, Image, Voice, At, Startup
from mirai.models import NudgeEvent, MemberHonorChangeEvent, MemberCardChangeEvent, MemberSpecialTitleChangeEvent

from plugins.RandomStr import random_str
from plugins.newLogger import newLogger
from plugins.translater import translate
from run import poeAi, voiceReply, nudgeReply, blueArchiveHelper, imgSearch, extraParts, wReply, userSign, groupManager, \
    PicRandom, musicShare

if __name__ == '__main__':
    with open('config.json','r',encoding='utf-8') as fp:
        data=fp.read()
    config=json.loads(data)
    qq=int(config.get('botQQ'))
    key=config.get("vertify_key")
    port= int(config.get("port"))
    bot = Mirai(qq, adapter=WebSocketAdapter(
        verify_key=key, host='localhost', port=port
    ))
    botName = config.get('botName')
    master=int(config.get('master'))


    #芝士logger
    logger=newLogger()

    #读取api列表
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    app_id = result.get("youdao").get("app_id")
    app_key=result.get("youdao").get("app_key")#有道翻译api
    sizhiKey=result.get("siZhiAi")
    proxy=result.get("proxy")
    moderate=result.get("moderate")
    logger.info("读取到apiKey列表")

    global notice
    notice=0
    @bot.on(GroupMessage)
    async def unlockNotice(event:GroupMessage):
        global notice
        if str(event.message_chain)=="notice" and event.sender.id==master:
            notice=1
    async def sendNotice(event:GroupMessage):
        global notice
        if notice==1 and event.sender.id==master:
            notice=0
            file = open('data/music/groups.txt', 'r')
            js = file.read()
            severGroupsa = json.loads(js)
            for i in severGroupsa:
                await bot.send(int(i),(event.message_chain,"\n随机码："+random_str()))


    '''@bot.on(GroupMessage)
    async def imgGet(event:GroupMessage):
        if event.message_chain.count(Image):
            lst_img = event.message_chain.get(Image)
            for i in lst_img:
                img_url = i.url
                print(img_url)'''


    # 菜单
    @bot.on(GroupMessage)
    async def help(event: GroupMessage):
        if ('帮助' in str(event.message_chain) or '菜单' in str(event.message_chain)) and At(bot.qq) in event.message_chain:
            logger.info("获取菜单")
            await bot.send(event, Image(path='config/help1.png'))
            await bot.send(event, Image(path='config/help2.png'))
            await bot.send(event, '这是' + botName + '的功能列表\nヾ(≧▽≦*)o')
        if '制图' in str(event.message_chain) and At(bot.qq) in event.message_chain :
            logger.info("菜单")
            await bot.send(event, Image(path='config/picMaker.png'))
            await bot.send(event, '这是' + botName + '的制图功能列表\nヾ(≧▽≦*)o')
    @bot.on(GroupMessage)
    async def clearCache(event:GroupMessage):
        if event.sender.id==master and str(event.message_chain)=="/clearcache":
            logger.info("执行清理缓存操作")
            ls1=os.listdir("data/pictures/avatars")
            for i in ls1:
                try:
                    os.remove("data/pictures/avatars/"+i)
                except:
                    continue
            logger.info("清理头像缓存完成")
            ls1 = os.listdir("data/pictures/cache")
            for i in ls1:
                try:
                    os.remove("data/pictures/cache/" + i)
                except:
                    continue
            logger.info("清理缓存完成")
            ls1 = os.listdir("data/pictures/wallpaper")
            for i in ls1:
                try:
                    os.remove("data/pictures/wallpaper/" + i)
                except:
                    continue
            logger.info("清理图片缓存完成")

    @bot.on(Startup)
    async def clearCache(event:Startup):
        logger.info("执行清理缓存操作")
        ls1 = os.listdir("data/pictures/avatars")
        for i in ls1:
            try:
                os.remove("data/pictures/avatars/" + i)
            except:
                continue
        logger.info("清理头像缓存完成")
        ls1 = os.listdir("data/pictures/cache")
        for i in ls1:
            try:
                os.remove("data/pictures/cache/" + i)
            except:
                continue
        logger.info("清理缓存完成")
    try:
        logger.info("检查github更新")
        os.system("git pull https://github.com/avilliai/Manyana.git")
        logger.info("自动从github更新完成")
    except:
        logger.error("自动从github更新失败，请检查网络代理")
    subprocess.Popen(["python.exe", "flask_voice.py"],cwd="vits")
    #asyncio.run(os.system("cd vits && python flask_voice.py"))
    logger.info(" 语音合成sever启动....")

    def startVer():
        file_object = open("config/mylog.log")
        try:
            all_the_text = file_object.read()
        finally:
            file_object.close()
        print(all_the_text)

    voiceReply.main(bot,app_id,app_key,logger)#语音生成
    if proxy!="":
        try:
            logger.info("开发过程中暂不启动poe-api")
            #poeAi.main(bot,master,result.get("poe-api"),result.get("proxy"),logger)#poe-api
        except:
            logger.error("poe-api启动失败")
        imgSearch.main(bot, result.get("sauceno-api"), result.get("proxy"), logger)
    else:
        logger.warning("未设置代理，禁用poe-api与搜图")
    nudgeReply.main(bot,app_id,app_key,logger)#戳一戳
    extraParts.main(bot,result.get("weatherXinZhi"),logger)#额外小功能
    wReply.main(bot,config,sizhiKey,app_id,app_key,logger)
    blueArchiveHelper.main(bot,app_id,app_key,logger)
    userSign.main(bot,result.get("weatherXinZhi"),logger)
    groupManager.main(bot,config,moderate,logger)
    PicRandom.main(bot,logger)
    musicShare.main(bot,master,botName,logger)
    startVer()

    bot.run()