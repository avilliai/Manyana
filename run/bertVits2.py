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
from plugins.modelsLoader import modelLoader
from plugins.translater import translate
from plugins.vitsGenerate import voiceGenerate, taffySayTest


def main(bot,logger,berturl,proxy):
    logger.info("bert_vits语音合成用户端启动....")
    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    spe=result.get("bert_speakers")

    @bot.on(GroupMessage)
    async def taffySay(event:GroupMessage):

        if "说" in str(event.message_chain) and str(event.message_chain).split("说")[0] in spe:
            data={}

            data["speaker"]=str(event.message_chain).split("说")[0]
            data["text"]=str(event.message_chain).replace(str(event.message_chain).split("说")[0]+"说","")
            path=await taffySayTest(data,berturl,proxy)
            await bot.send(event,Voice(path=path))