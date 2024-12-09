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
from plugins.toolkits import send_like,delete_msg


def main(bot,logger,master):
    @bot.on(GroupMessage)
    async def like(event: GroupMessage):
        if str(event.message_chain) == '赞我':
            try:
                await send_like(event.sender.id)
                await bot.send(event,'已赞你',True)
            except:
                await bot.send(event,'赞失败',True)
    
    @bot.on(GroupMessage)
    async def chehui(event: GroupMessage):
        if str(event.message_chain) == '撤回' and event.sender.id == master:
            msg = event.json()
            event_dict = json.loads(msg)
            has_quote = any(element.get('type') == 'Quote' for element in event_dict.get('message_chain', []))
            if has_quote:
                quote_id = next((element['id'] for element in event_dict['message_chain']
                                if element.get('type') == 'Quote'), None)
                try:
                    await delete_msg(quote_id)
                except:
                    await bot.send(event,'撤回失败',True)

        
                
                
                
                
