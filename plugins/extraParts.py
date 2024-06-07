# -*- coding: utf-8 -*-
import random
import json
from io import BytesIO

from emoji import is_emoji
import httpx
from PIL import Image

from plugins.RandomStr import random_str


def get_cp_mesg(gong, shou):
    with open('data/autoReply/cp.json', "r", encoding="utf-8") as f:
        cp_data = json.loads(f.read())
    return random.choice(cp_data['data']).replace('<攻>', gong).replace('<受>', shou)
async def emojimix(emoji1,emoji2):
    if is_emoji(emoji1) and is_emoji(emoji2):
        pass
    else:
        print("not emoji")
        return None
    url=f"http://promptpan.com/mix/{emoji1}/{emoji2}"
    #url=f"https://emoji6.com/emojimix/?emoji={emoji1}+{emoji2}"
    path = "data/pictures/cache/" + random_str() + ".png"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url)
        #print(r.content)
        with open(path,"wb") as f:
            f.write(r.content)# 从二进制数据创建图片对象
        # print(path)
        return path
