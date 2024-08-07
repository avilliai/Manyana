import re
import httpx
import asyncio
import time
import datetime
from PIL import Image
import io
from mirai import logger

'''
steam查询相关功能
'''
async def fetch_description(keyword):
    url = f'https://baike.baidu.com/item/{keyword}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    async with httpx.AsyncClient(timeout=100) as client:
        response = await client.get(url, headers=headers)
        if response.is_redirect:
            redirect_url = response.headers.get('Location')
            response = await client.get(f'https://baike.baidu.com{redirect_url}', headers=headers)
        html_content = response.text
        
    # logger.info("xxxxxxxxxxx##########")
    # logger.info(response.text)
    match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html_content)
    
    return match.group(1) if match else "没找到游戏描述喵~"


async def get_steam_game_description(game_id,proxy=None):
    url = f"https://store.steampowered.com/app/{game_id}/"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
        "referer": "https://steamstats.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36",
    }
    async with httpx.AsyncClient(timeout=200,verify=False,proxies={"http://": proxy, "https://": proxy} if proxy else None) as client:
        response = await client.get(url,headers=headers)
        html = response.text
    
    description = re.findall(r'<div class="game_description_snippet">(.*?)</div>', html, re.S)
    if len(description) == 0:
        return "none"
    return description[0].strip()

async def get_steam_game_search(keyword,proxy=None):
    url = f"https://steamstats.cn/api/steam/search?q={keyword}&page=1&format=json&lang=zh-hans"
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6",
        "referer": "https://steamstats.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36",
    }

    async with httpx.AsyncClient(timeout=200,proxies={"http://": proxy, "https://": proxy} if proxy else None) as client:
        response = await client.get(url, headers=headers)
        result = response.json()

    if len(result["data"]["results"]) == 0:
        print(f"搜索不到{keyword}呢~检查下有没有吧~搜英文名的效果可能会更好喵~")
        return None
    
    return result["data"]["results"][0]

async def solve(keyword,proxy=None):
    # logger.info("选择代理：" + proxy)
    search_result = await get_steam_game_search(keyword,proxy)
    if search_result:
        img_url = search_result["avatar"]
        async with httpx.AsyncClient(timeout=200,proxies={"http://": proxy, "https://": proxy} if proxy else None,verify=False) as client:
            response = await client.get(img_url)
            img_content = response.content
        image = Image.open(io.BytesIO(img_content))
        path = f"data/pictures/cache/{search_result['name']}.png"
        image.save(path)
        description = await get_steam_game_description(search_result["app_id"],proxy)
        if(description == 'none'):
            description = await fetch_description(keyword)
        result_dict = {
            "name": search_result['name'],
            "name_cn": search_result['name_cn'],
            "app_id": search_result['app_id'],
            "description": description,
            "steam_url": f"https://store.steampowered.com/app/{search_result['app_id']}/",
            "path": path
        }
        return result_dict


