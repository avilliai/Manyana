# -*- coding:utf-8 -*-
import datetime
import json
import os
import random
import re
import urllib
from asyncio import sleep

import yaml
from mirai import Image, Voice, Startup
from mirai import Mirai, WebSocketAdapter, FriendMessage, GroupMessage, At, Plain

def main(bot,logger):

    @bot.on(GroupMessage)
    async def meme(event: GroupMessage):
        global memeData
        if str(event.message_chain) == "meme":
            la = os.listdir("data/pictures/meme")
            la = "data/pictures/meme/" + random.choice(la)
            await bot.send(event, (str(event.sender.member_name) + "抽取到了：", Image(path=la)))

