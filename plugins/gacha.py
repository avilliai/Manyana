import datetime
import os.path
import random

import httpx
import asyncio

import requests
import yaml
from PIL import Image
from io import BytesIO

from plugins.RandomStr import random_str


def get_headers():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

    userAgent = random.choice(user_agent_list)
    headers = {'User-Agent': userAgent}
    return headers


async def arkGacha():
    headers = get_headers()
    url="http://api.elapsetower.com/arknightsdraw"

    path="data/pictures/cache/"+random_str()+".png"
    #path="moyu.png"
    #print(path)
    if os.path.exists(path):
        return path
    else:
        async with httpx.AsyncClient(timeout=20,headers=headers) as client:
            r = await client.get(url)
            img = Image.open(BytesIO(r.content))  # 从二进制数据创建图片对象
            img.save(path)  # 使用PIL库保存图片
            #print(path)
            return path
async def starRailGacha():
   with open('data/GachaData/StarRail.yaml', 'r', encoding='utf-8') as file:
     students= yaml.load(file, Loader=yaml.FullLoader)

   i = 0
   character = []

   while i < 10:
     if i==0:
        ass = random.randint(1, 150)
        if ass < 75:
            cha = random.choice(list(students.get("四星角色").keys()))
        else:
            cha = random.choice(list(students.get("四星光锥").keys()))
        character.append(cha)
     else:
        ass = random.randint(1, 150)
        if ass < 4:
         if ass < 2:
             cha = random.choice(list(students.get("五星角色").keys()))
         else:
             cha = random.choice(list(students.get("五星光锥").keys()))
         # print(cha)
         character.append(cha)
        if ass > 3 and ass < 40:
         if ass < 20:
             cha = random.choice(list(students.get("四星角色").keys()))
         else:
             cha = random.choice(list(students.get("四星光锥").keys()))
         character.append(cha)
        if ass > 39:
         cha = random.choice(list(students.get("三星光锥").keys()))
         # print(cha)
         character.append(cha)
     i += 1

   # print(character)
   a = 193
   b = 221
   count = 0
   st = Image.open('data/GachaData/StarRail/bg.png')
   path ="data/pictures/cache/"+random_str() + '.png'
   for i in character:
     # 剪切图像
     # 发起超级融合

     st2 = Image.open("data/GachaData/StarRail/" + i + ".png")

     im = st
     mark = st2
     layer = Image.new('RGBA', im.size, (0, 0, 0, 0))
     # print(str(a)+'------'+str(b))
     layer.paste(mark, (a, b))
     a += 473
     count += 1
     if count == 5:
         b += 689
         a = 193
     out = Image.composite(layer, im, layer)
     st=out
   #st.show()
   st.save(path)
   #print(path)
   return path
if __name__ == '__main__':
    #asyncio.run(arkGacha())
    asyncio.run(starRailGacha())