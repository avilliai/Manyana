# -*- coding: utf-8 -*-
import asyncio
import json
import os
import datetime
import random
import re
import time
import sys
import socket

import httpx
import requests
import utils
import yaml
from mirai import Image, Voice
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

from plugins.RandomStr import random_str

from plugins.modelsLoader import modelLoader
from plugins.picGet import pic
from plugins.translater import translate



def main(bot,logger):
    logger.info("额外的功能 启动完成")

    @bot.on(GroupMessage)
    async def handle_group_message(event: GroupMessage):
        # if str(event.message_chain) == '/pic':

        if '/pic' in str(event.message_chain):
            picNum = int((str(event.message_chain))[4:])
        elif "@"+str(bot.qq) in str(event.message_chain):
            picNum=int(get_number(str(event.message_chain).replace("@"+str(bot.qq),"")))
        else:
            return
        logger.info("图片获取指令....数量："+str(picNum))
        if picNum < 10 and picNum > -1:
            for i in range(picNum):
                logger.info("获取壁纸")
                a = pic()
                await bot.send(event, Image(path=a))
        elif picNum == '':
            a = pic()
            await bot.send(event, Image(path=a))
        else:
            await bot.send(event, "数字超出限制")
        logger.info("图片获取完成")

    # 整点正则
    pattern = r".*(壁纸|图|pic).*(\d+).*|.*(\d+).*(壁纸|图|pic).*"

    # 定义一个函数，使用正则表达式检查字符串是否符合条件，并提取数字
    def get_number(string):
        # 使用re.match方法，返回匹配的结果对象
        match = re.match(pattern, string)
        # 如果结果对象不为空，返回捕获的数字，否则返回None
        if match:
            # 如果第二个分组有值，返回第二个分组，否则返回第三个分组
            if match.group(2):
                return match.group(2)
            else:
                return match.group(3)
        else:
            return None