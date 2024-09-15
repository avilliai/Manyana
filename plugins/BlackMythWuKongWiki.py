# -*- coding: utf-8 -*-
import asyncio

import httpx

from plugins.toolkits import get_headers, random_str, picDwn
from bs4 import BeautifulSoup
from mirai import FriendMessage, GroupMessage, At, Plain,MessageChain,Startup,Image
async def wukongwiki(aim,action=False):
    mesChain=[]
    async with httpx.AsyncClient(headers=get_headers(),timeout=20,verify=False) as client:
        r = await client.get(f"https://wiki.biligame.com/wukong/{aim}")
        soup = BeautifulSoup(r.text, 'html.parser')
        #解析并获取影神图
        results = soup.select("#精怪图示-影神图 > div > div")
        for result in results:
            img_tag = result.find('img')
            if img_tag:
                src_value = img_tag['src']
                p=await picDwn(src_value,f"data/pictures/cache/{random_str()}.jpg")

        #解析影神图配诗
        poem_div = soup.select_one("#mw-content-text > div > div.wk-poem")
        all_text = poem_div.text.strip()
        #影神图介绍
        target_div = poem_div.find_next_sibling("div")
        target_text = target_div.text.strip()
        mesChain.append([Image(path=p), Plain(all_text+"\n"+target_text)])
        #原著出处
        try:
            p=target_div.find_next_sibling("p")
            target_div = target_div.find_next_sibling("div")
            target_text = target_div.text.strip()
            mesChain.append([Plain(p.text.strip()+"\n"+target_text)])
        except:
            pass #马夸的
        if action:
            #技能招式
            p = target_div.find_next_sibling("p").find_next_sibling("p")
            mesChain.append([Plain(p.text.strip())])
            div_boxes = soup.find_all('div', class_='div-box')
            for div_box in div_boxes:
                try:
                    fashu_names = div_box.find('div', class_='fashu-name').text.strip()
                    fashu_block = div_box.find('div', class_='fashu-blocks').find('p')
                    try:
                        gif500px_href = div_box.find('div', class_='gif500px').find('img')['src']
                        p = await picDwn(gif500px_href, f"data/pictures/cache/{random_str()}.gif")
                    except:
                        p="data/colorfulAnimeCharacter/2ab85edd7c1e98b1906ce9e11723cd80_aio.png"

                    if fashu_names:
                        pass
                    else:
                        fashu_names=""
                    if fashu_block:
                        fashu_block=fashu_block.text.strip()
                    else:
                        fashu_block=""
                    mesChain.append([Plain(fashu_names+"\n"+fashu_block),Image(path=p)])
                except:
                    continue
        return mesChain
