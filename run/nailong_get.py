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

from plugins.toolkits import random_str
from plugins.nailong11.nailong import main as nailong_main

def main(bot, logger):
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
            lst_img = event.message_chain.get(Image)
            img_url = lst_img[0].url
            b64_in = await url_to_base64(img_url)
            check = await nailong_main(b64_in)
            if check == 1:
                await bot.send(event, f"爱发奶龙的小朋友你好啊~",True)