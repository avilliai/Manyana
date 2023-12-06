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
from plugins.cloudMusic import cccdddm


def main(bot,logger):
    logger.warning("语音点歌 loaded")
    @bot.on(GroupMessage)
    async def selectMusic(event: GroupMessage):
        if str(event.message_chain).startswith("点歌 "):
            musicName=str(event.message_chain).replace("点歌 ","")
            logger.info("点歌："+musicName)
            try:
                ffs=await cccdddm(musicName)
                if ffs==None:
                    await bot.send(event,"连接出错，或无对应歌曲")
                else:
                    await bot.send(event,Voice(path=ffs))
            except:
                await bot.send(event, "连接出错，或无对应歌曲")
