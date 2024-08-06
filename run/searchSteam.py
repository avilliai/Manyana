# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
from asyncio import sleep
from io import BytesIO

import httpx
import requests
import yaml
from PIL import Image as Image1
from mirai import GroupMessage, At, Plain
from mirai import Image, Voice, Startup, MessageChain
from mirai.models import ForwardMessageNode, Forward
from plugins.solveSearch import solve

def main(bot,logger):
    logger.info("steam查询插件启动")
    with open('config/api.yaml', 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
    proxy = result.get("proxy")
    @bot.on(GroupMessage)
    async def searchGame(event:GroupMessage):
        if(str(event.message_chain).startswith("steam查询")):
            keyword = str(event.message_chain).replace("steam查询","")
            try:
                logger.info(f"查询游戏{keyword}")
                result_dict = await solve(keyword)
                if(result_dict is None):
                    await bot.send(event, "没有找到哦，试试其他名字~")
                    return
                logger.info(result_dict)
                text = "游戏："
                text = text + result_dict['name'] + f"({result_dict['name_cn']})" + "\n游戏id：" + str(result_dict['app_id']) + "\n游戏描述：" + f"{result_dict['description']}\nSteamUrl：" + f"{result_dict['steam_url']}"
                await bot.send(event, (Image(path=result_dict['path']), text))
            except Exception as e:
                logger.error(e)
                logger.exception("详细错误如下：")
                await bot.send(event,"查询失败")


