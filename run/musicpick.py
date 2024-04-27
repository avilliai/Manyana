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
from mirai.models import MusicShare

from plugins.cloudMusic import cccdddm, musicDown


def main(bot,logger):
    logger.warning("语音点歌 loaded")
    global musicTask
    musicTask={}
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        resulta = yaml.load(f.read(), Loader=yaml.FullLoader)
    musicToVoice=resulta.get("musicToVoice")
    @bot.on(GroupMessage)
    async def selectMusic(event: GroupMessage):
        global musicTask
        if str(event.message_chain).startswith("点歌 "):
            musicName=str(event.message_chain).replace("点歌 ","")
            logger.info("点歌："+musicName)
            try:
                ffs=await cccdddm(musicName)
                if ffs==None:
                    await bot.send(event,"连接出错，或无对应歌曲")
                else:
                    musicTask[event.sender.id]=ffs
                    #print(ffs)
                    t="请发送序号："
                    i=0
                    for sf in ffs:
                        t=t+"\n"+str(i)+" "+sf[0]+" | "+sf[3]
                        i+=1
                    await bot.send(event,t,True)
            except:
                await bot.send(event, "连接出错，或无对应歌曲")

    @bot.on(GroupMessage)
    async def select11Music(event: GroupMessage):
        global musicTask
        if event.sender.id in musicTask:
            try:
                ass=musicTask.get(event.sender.id)[int(str(event.message_chain))]

                logger.info("获取歌曲："+ass[0])
                if musicToVoice==True:
                    p = await musicDown(ass[1], ass[0])
                    await bot.send(event, Voice(path=p))
                else:
                    await bot.send(event, MusicShare(kind="NeteaseCloudMusic", title=ass[0],
                                                                      summary=ass[3],
                                                                      jump_url="http://music.163.com/song/media/outer/url?id=" + str(ass[1]) + ".mp3",
                                                                      picture_url=ass[2],
                                                                      music_url="http://music.163.com/song/media/outer/url?id=" + str(ass[1]) + ".mp3",
                                                                      brief=ass[3]))
                    musicTask.pop(event.sender.id)
            except:
                musicTask.pop(event.sender.id)
                await bot.send(event,"点歌失败！不规范的操作")

