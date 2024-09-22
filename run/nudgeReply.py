# -*- coding: utf-8 -*-
import random

import yaml
from mirai import GroupMessage
from mirai import Poke
from mirai.models import NudgeEvent


def main(bot, master, logger, berturl, proxy):
    with open('config/nudgeReply.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    normal_Reply = result.get("nudgedReply")
    special_Reply = result.get("BeatNudge")
    special_Reply1 = result.get("BeatNudge1")
    global transLateData
    with open('data/autoReply/transLateData.yaml', 'r', encoding='utf-8') as file:
        transLateData = yaml.load(file, Loader=yaml.FullLoader)
    prob = result.get("prob")
    logger.info("读取到apiKey列表")

    with open('config/settings.yaml', 'r', encoding='utf-8') as f:
        result0 = yaml.load(f.read(), Loader=yaml.FullLoader)
    speaker92 = result0.get("语音功能设置").get("speaker")
    voicegg = result0.get("语音功能设置").get("voicegenerate")
    nudgeornot = result0.get("chatGLM").get("nudgeReply")
    logger.info("语音合成模式：" + voicegg + " 语音合成speaker：" + speaker92)

    @bot.on(NudgeEvent)
    async def NudgeReply(event: NudgeEvent):
        global transLateData
        if event.target == bot.qq and not nudgeornot:
            logger.info("接收到来自" + str(event.from_id) + "的戳一戳")
            if random.randint(0, 100) > 100 - prob:
                await bot.send_group_message(event.subject.id, random.choice(special_Reply))
                try:
                    await bot.send_nudge(target=event.from_id, subject=event.subject.id, kind='Group')
                    await bot.send_group_message(event.subject.id, random.choice(special_Reply1))
                except:
                    try:
                        await bot.send_group_message(event.subject.id, Poke(name="ChuoYiChuo"))
                        await bot.send_group_message(event.subject.id, random.choice(special_Reply1))
                    except:
                        await bot.send_group_message(event.subject.id, "唔....似乎戳不了你呢....好可惜")
            else:
                rep = random.choice(normal_Reply)
                await bot.send_group_message(event.subject.id, rep)
