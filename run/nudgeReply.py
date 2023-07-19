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
from mirai import Image, Voice, Poke
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain
from mirai.models import NudgeEvent

from plugins.RandomStr import random_str
from plugins.modelsLoader import modelLoader
from plugins.translater import translate


def main(bot,logger):
    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    normal_Reply = result.get("nudgedReply")
    special_Reply = result.get("BeatNudge")
    special_Reply1 = result.get("BeatNudge1")
    prob=result.get("prob")
    logger.info("读取到apiKey列表")

    @bot.on(NudgeEvent)
    async def NudgeReply(event:NudgeEvent):
        if event.target==bot.qq:
            rep=random.choice(normal_Reply)
            logger.info("接收到来自"+str(event.from_id)+"的戳一戳")
            logger.info("回复："+rep)
            await bot.send_group_message(event.subject.id,rep)
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



