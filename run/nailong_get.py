import os
import random
import httpx
import json
import base64
from io import BytesIO
from PIL import Image as PILImage
import asyncio
import re

import yaml
from mirai import GroupMessage
from mirai import Image

from plugins.toolkits import random_str, delete_msg
from plugins.nailong11.nailong import main as nailong_main

def main(bot, logger):
    with open('config/controller.yaml', 'r', encoding='utf-8') as f:
        controller = yaml.load(f.read(), Loader=yaml.FullLoader)
    sets = controller.get("奶龙检测")
    chehui = sets.get("是否撤回")
    if_nailong = sets.get("开关")
    if if_nailong:
        async def get_group_member_info(group_id: int, user_id: int):
            url = "http://localhost:3000/get_group_member_info"
            payload = {
                "group_id": group_id,
                "user_id": user_id
            }
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ff',
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                else:
                    response.raise_for_status()

        async def is_group_admin(group_id: int, user_id: int) -> bool:
            try:
                member_info = await get_group_member_info(group_id, user_id)
                role = member_info.get('data', {}).get('role', '')
                return role == 'admin' or role == 'owner'
            except Exception as e:
                print(f"An error occurred while checking admin status: {e}")
                return False
        
        async def url_to_base64(url):
            async with httpx.AsyncClient(timeout=9000) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    image_bytes = response.content
                    encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                    return encoded_string
                else:
                    raise Exception(f"Failed to retrieve image: {response.status_code}")
        
        @bot.on(GroupMessage)
        async def get_pic(event: GroupMessage):
            is_group_admin1 = await is_group_admin(event.group.id, bot.qq)
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            b64_in = await url_to_base64(img_url)
            check = await nailong_main(b64_in)
            if check == 1:
                if chehui and is_group_admin1:
                    msg = event.json()
                    event_dict = json.loads(msg)
                    Source_id = next((element['id'] for element in event_dict['message_chain']
                                    if element.get('type') == 'Source'), None)
                    await delete_msg(Source_id)
                    await bot.send(event, f"爱发奶龙的小朋友你好啊~我是贝利亚",True)
                elif chehui and is_group_admin1 == False:
                    await bot.send(event, f"如果我是管理就给你撤了",True)
                else:
                    await bot.send(event, f"爱发奶龙的小朋友你好啊~",True)