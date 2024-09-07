# -*- coding: utf-8 -*-
import os
import random

import yaml
import httpx
from bs4 import BeautifulSoup
from fuzzywuzzy import process
from mirai import GroupMessage, At
from mirai import Voice
from mirai.models import MusicShare

from itertools import repeat

from plugins import weatherQuery

import datetime
import json

import re
from asyncio import sleep
from io import BytesIO
import requests
from PIL import Image as Image1
from mirai import GroupMessage, At, Plain
from mirai import Image, Voice, Startup, MessageChain
from mirai.models import ForwardMessageNode, Forward

from plugins.toolkits import random_str,picDwn
from mirai import Mirai, WebSocketAdapter, GroupMessage, Image, At, Startup, FriendMessage, Shutdown,MessageChain

#master=1270858640


# 创建文件夹并保存数据的函数
def save_data(group_id, data):
    folder_path = f"data/aite/{group_id}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, 'group_data.yaml')
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, allow_unicode=True)

# 读取群数据的函数
def load_data(group_id):
    file_path = f"data/{group_id}/group_data.yaml"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    return {}

# 处理订阅和取消订阅的函数
def update_subscription(group_id, user_id, xx, status):
    data = load_data(group_id)
    if xx not in data:
        data[xx] = {}
    data[xx][user_id] = status
    save_data(group_id, data)

# 处理大召唤阵的函数
def summon(group_id, xx):
    data = load_data(group_id)
    if xx in data:
        subscribed_users = [user_id for user_id, status in data[xx].items() if status == 1]
        return subscribed_users
    return []



def main(bot, logger):
    # 监听群消息
    @bot.on(GroupMessage)
    async def group_message_handler(event: GroupMessage):
        group_id = event.group.id
        user_id = event.sender.id
        message = event.message_chain.get(Plain)[0].text.strip()

        # 处理 "创建大召唤阵 XX"
        if str(event.message_chain).startswith("创建大召唤阵"):
            xx = message.split("创建大召唤阵")[-1].strip()
            data = load_data(group_id)
            if xx not in data:
                data[xx] = {}
                save_data(group_id, data)
            await bot.send(event, f"已创建大召唤阵: {xx}")

        # 处理 "订阅 XX"
        elif str(event.message_chain).startswith("订阅"):
            xx = message.split("订阅")[-1].strip()
            update_subscription(group_id, user_id, xx, 1)
            await bot.send(event, f"{user_id} 已订阅 {xx}")

        # 处理 "取消订阅 XX"
        elif str(event.message_chain).startswith("取消订阅"):
            xx = message.split("取消订阅")[-1].strip()
            update_subscription(group_id, user_id, xx, 0)
            await bot.send(event, f"{user_id} 已取消订阅 {xx}")

        # 处理 "大召唤阵 XX"
        elif str(event.message_chain).startswith("大召唤阵"):
            xx = message.split("大召唤阵")[-1].strip()
            subscribed_users = summon(group_id, xx)
            if subscribed_users:
                at_users = [At(user_id=user) for user in subscribed_users]
                await bot.send(event, [Plain(f"大召唤阵: {xx}\n"), *at_users])
            else:
                await bot.send(event, f"没有订阅 {xx} 的用户")
         
     
        
        
        
        



    
    
    
    