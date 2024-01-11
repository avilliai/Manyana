# -*- coding:utf-8 -*-
import datetime
import json
import os
import random
import re
import urllib
from asyncio import sleep
from io import BytesIO

import httpx
import requests
import yaml

from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import File

from plugins.RandomStr import random_str
from plugins.tarot import tarotChoice
from PIL import Image as Image1

from plugins.vitsGenerate import sovits, edgetts


def main(bot,logger):
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    speaker = result.get("chatGLM").get("speaker")
    speakers=result.get("so_vits_speakers")
    @bot.on(GroupMessage)
    async def sovitsHelper(event: GroupMessage):
        if str(event.message_chain).startswith("/sovits"):

            bsf=str(event.message_chain).replace("/sovits","")
            logger.info("sovits文本推理任务：" + bsf)
            r=await sovits({"text":bsf,"speaker":"riri"})
            logger.info("tts 完成")
            await bot.send(event,Voice(path=r))
    @bot.on(GroupMessage)
    async def edgettsHelper(event: GroupMessage):
        if str(event.message_chain).startswith("/edgetts"):

            bsf=str(event.message_chain).replace("/edgetts","")
            logger.info("edgetts文本推理任务：" + bsf)
            r=await edgetts({"text":bsf,"speaker":speaker})
            logger.info("edgetts 完成")
            await bot.send(event,Voice(path=r))
    '''@bot.on(GroupMessage)
    async def voicetrans(event: GroupMessage):
        if Voice in event.message_chain and event.sender.id==1840094972:
            print("ok")
            v=event.message_chain.get(Voice)
            #p=v[0].url
            #print(p)
            await Voice.download(v[0], 'data/voices/rest.silk')
            silkcoder.decode("data/voices/rest.silk", "data/voices/rest.wav",
                             ffmpeg_para=["-ar", "44100"])
            #print('over')
            r = await sovits({"text": "", "speaker": "riri","voice":""})
            await bot.send(event, Voice(path=r))'''
    '''@bot.on(GroupMessage)
    async def voicetrans(event: GroupMessage):
        if Voice in event.message_chain and event.sender.id==1840094972:
            print("ok")
            v = event.message_chain.get(Voice)
            # p=v[0].url
            # print(p)
            path = random_str() + ".silk"
            await Voice.download(v[0], 'data/voices/' + path)
            silkcoder.decode('data/voices/' + path, str('data/voices/' + path).replace(".silk",".wav"),
                             ffmpeg_para=["-ar", "44100"])
            path = os.path.abspath(os.curdir) + "/data/voices/" + path
            print(path)
            # print('over')
            # print(v[0].url.replace("\n",""))
            r = await sovits({"text": "", "speaker": "riri", "voice": path.replace(".silk",".wav")})
            await bot.send(event, Voice(path=r))'''


